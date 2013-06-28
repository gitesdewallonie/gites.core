# -*- coding: utf-8 -*-
import json
import hashlib
from five import grok
from Acquisition import Explicit
from Products.Maps.interfaces import IMarker
from zope import interface, component
from affinitic.db.cache import FromCache
from zope.contentprovider.interfaces import IContentProvider
from plone.memoize.instance import memoize
from gites.db import session
from gites.db.content import Metadata, Commune, Hebergement
from gites.core.content.interfaces import IPackage
from gites.core.interfaces import IHebergementsFetcher, IHebergementInSearch
from Products.CMFPlone.interfaces import IPloneSiteRoot
from gites.locales import GitesMessageFactory as _
from gites.core.adapters.hebergementsfetcher import getGeocodedLocation

grok.templatedir('templates')
grok.context(interface.Interface)


class HebergementUpdateListing(grok.View):
    grok.context(interface.Interface)
    grok.name('update_listing')

    def render(self):
        renderer = component.getMultiAdapter((self.context, self.request, self),
                                             IContentProvider, name='gites.heblisting')
        if isinstance(renderer, Explicit):
            renderer = renderer.__of__(self.context)
        rendered_viewlets = []
        renderer.update()
        for viewlet in renderer.viewlets:
            rendered_viewlets.append(viewlet.render())
        self.request.environ['plone.transformchain.disable'] = True
        return u'\n'.join(rendered_viewlets)


LINKS_COUNT = 5


class HebergementListingForm(grok.Viewlet):
    grok.order(10)
    grok.context(IPackage)

    def filters(self):
        userCriteria = self.context.userCriteria
        query = session().query(Metadata).filter(Metadata.met_pk.in_(userCriteria))
        return query.all()

    @memoize
    def count_hebs(self, metadata_id):
        fetcher = component.getMultiAdapter((self.context, self.view,
                                            self.request),
                                            IHebergementsFetcher)
        subquery = fetcher._query.subquery()
        from gites.db import session
        from gites.db.content import LinkHebergementMetadata
        query = session().query(LinkHebergementMetadata.heb_fk)
        query = query.options(FromCache('gdw'))
        query = query.filter(LinkHebergementMetadata.link_met_value == True)
        query = query.filter(LinkHebergementMetadata.metadata_fk == metadata_id)
        query = query.filter(LinkHebergementMetadata.heb_fk == subquery.c.heb_pk)
        return query.count()


class HebergementInSearchListingView(grok.View):
    grok.context(IHebergementInSearch)
    grok.name('view')

    def heb_type_type(self):
        return self.context.heb_type_type

    def heb_type(self):
        return self.context.heb_type

    def heb_type_trad(self):
        return _(self.context.heb_type)

    def nombre_epis(self):
        return self.context.heb_nombre_epis

    def render(self):
        return None


class HebergementInListingView(grok.View):
    grok.context(Hebergement)
    grok.name('view')

    def heb_type_type(self):
        return self.context.type.type_heb_type

    def heb_type_trad(self):
        return self.heb_type()

    def heb_type(self):
        lang = self.request.get('LANGUAGE')
        return self.context.type.getTitle(languageCode=lang)

    def nombre_epis(self):
        return self.context.epis[0].heb_nombre_epis

    def render(self):
        return None


class HebergementsInListing(grok.Viewlet):
    grok.order(20)
    grok.baseclass()
    grok.template('hebergementsinlisting')

    @property
    def _fetcher(self):
        return component.getMultiAdapter((self.context, self.view,
                                         self.request),
                                         IHebergementsFetcher)

    def hebergements(self):
        return self._fetcher()

    def is_geolocalized(self):
        return (component.queryAdapter(self.context, IMarker) is not None and
                self.context.getRange() is not None)

    @memoize
    def count(self):
        return len(self._fetcher)

    def next_items(self):
        next_size = LINKS_COUNT + (LINKS_COUNT - len(self.previous_items()))
        return range(self.current_page() + 1, min(self.current_page() + next_size,
                                                  self.page_counts()))

    def current_page(self):
        return self._fetcher.selected_page()

    def current_item(self):
        return self._fetcher.selected_page() * self._fetcher.batch_size

    def previous_items(self):
        def positives(items):
            return [x for x in items if x >= 0]
        return positives(range(self.current_page() - LINKS_COUNT, self.current_page()))

    def page_counts(self):
        return self.count() / self._fetcher.batch_size + 1

    def pages(self):
        return range(self.page_counts())

    def show_batch(self):
        return len(self.previous_items()) > 0 or len(self.next_items()) > 0

    def batch_start(self):
        return self._fetcher.batch_start

    def batch_end(self):
        return min(self._fetcher.batch_end, self.count())

    def is_last_page(self):
        return self._fetcher.selected_page() == len(self.pages()) - 1

    def is_first_page(self):
        return self._fetcher.selected_page() == 0

    def sort_items(self):
        return {'pers_numbers': _("nombre_personnes", "Nombre de personne"),
                'room_count': _("nombre-chambres", "Nombre de chambres"),
                'epis': _(u"Epis")}


class HebergementsInPackageListing(HebergementsInListing):
    grok.context(IPackage)

    def sort_items(self):
        sortables = {
            'pers_numbers': _("nombre_personnes", "Nombre de personne"),
            'room_count': _("nombre-chambres", "Nombre de chambres"),
            'epis': _(u"Epis"),
            'heb_type': _(u"Hebergement Type")}
        if self.is_geolocalized():
            sortables['distance'] = _('Distance')
        return sortables

    def heb_distance(self, hebergement):
        return round(hebergement.distance / 1000, 2)


class HebergementsInCommuneListing(HebergementsInListing):
    grok.context(Commune)


class RechercheListing(HebergementsInListing):
    grok.context(IPloneSiteRoot)

    def sort_items(self):
        sortables = {
            'pers_numbers': _("nombre_personnes", "Nombre de personne"),
            'room_count': _("nombre-chambres", "Nombre de chambres"),
            'epis': _(u"Epis")}
        if self.is_geolocalized():
            sortables['distance'] = _('Distance')
        return sortables

    def heb_distance(self, hebergement):
        return round(hebergement.distance / 1000, 2)

    def is_geolocalized(self):
        near_to = self.request.form['nearTo']
        return getGeocodedLocation(near_to)


class HiddenRequestParameters(grok.Viewlet):
    grok.order(5)

    @property
    def params(self):
        return json.dumps(self.request.form)

    @property
    def hash(self):
        hash_json = json.dumps([self.context.absolute_url(),
                                self.request.form],
                               sort_keys=True)
        return hashlib.md5(hash_json).hexdigest()


class HebergementListingViewletManager(grok.ViewletManager):
    grok.name('gites.heblisting')

# register all viewlets in this viewlet manager:
grok.viewletmanager(HebergementListingViewletManager)
