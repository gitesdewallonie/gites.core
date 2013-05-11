# -*- coding: utf-8 -*-
import json
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
from gites.core.browser.moteur_recherche import MoteurRecherche
from Products.CMFPlone.interfaces import IPloneSiteRoot
from gites.locales import GitesMessageFactory as _

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

    def nombre_epis(self):
        return self.context.heb_nombre_epis

    def render(self):
        return None


class HebergementInListingView(grok.View):
    grok.context(Hebergement)
    grok.name('view')

    def heb_type_type(self):
        return self.context.type.type_heb_type

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

    def isGeoLocalized(self):
        return (component.queryAdapter(self.context, IMarker) is not None and
                self.context.getRange() is not None)

    @memoize
    def count(self):
        return len(self._fetcher)

    def pages(self):
        counts = self.count() / self._fetcher.batch_size + 1
        return range(counts)

    def show_batch(self):
        return len(self.pages()) > 1

    def batch_start(self):
        return self._fetcher.batch_start

    def batch_end(self):
        return self._fetcher.batch_end

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
        if self.isGeoLocalized():
            sortables['distance'] = _('Distance')
        return sortables

    def heb_distance(self, hebergement):
        return round(hebergement.distance / 1000, 2)


class HebergementsInCommuneListing(HebergementsInListing):
    grok.context(Commune)


class RechercheListing(HebergementsInListing):
    grok.view(MoteurRecherche)


class RechercheListing(HebergementsInListing):
    grok.context(IPloneSiteRoot)


class HiddenRequestParameters(grok.Viewlet):
    grok.order(5)

    @memoize
    def request_json_parameters(self):
        if self.request._file is None:
            return {}
        request_body = self.request._file.read()
        self.request._file.seek(0)
        try:
            return json.loads(request_body)
        except ValueError:
            return {}

    def parameters(self):
        params = self.request_json_parameters()
        params.update(self.request.form.items())
        return params.items()


class HebergementListingViewletManager(grok.ViewletManager):
    grok.name('gites.heblisting')

# register all viewlets in this viewlet manager:
grok.viewletmanager(HebergementListingViewletManager)
