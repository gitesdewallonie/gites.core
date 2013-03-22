# -*- coding: utf-8 -*-
from five import grok
from Acquisition import Explicit
from zope import interface, component
from affinitic.db.cache import FromCache
from zope.contentprovider.interfaces import IContentProvider
from plone.memoize.instance import memoize
from gites.db import session
from gites.db.content import Metadata
from gites.core.content.interfaces import IPackage
from gites.core.interfaces import IHebergementsFetcher
from gites.locales import GitesMessageFactory as _

grok.templatedir('templates')
grok.context(interface.Interface)


class HebergementUpdateListing(grok.View):
    grok.context(IPackage)
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


class HebergementsInListing(grok.Viewlet):
    grok.order(20)

    @property
    def _fetcher(self):
        return component.getMultiAdapter((self.context, self.view,
                                         self.request),
                                         IHebergementsFetcher)

    def hebergements(self):
        return self._fetcher()

    @memoize
    def count(self):
        return len(self._fetcher)

    def pages(self):
        return range(self.count() / self._fetcher.batch_size + 1)

    def batch_start(self):
        return self._fetcher.batch_start

    def batch_end(self):
        return self._fetcher.batch_end

    def is_last_page(self):
        return self._fetcher.selected_page() == len(self.pages()) - 1

    def is_first_page(self):
        return self._fetcher.selected_page() == 0

    def sort_items(self):
        return {'distance': _('Distance'),
                'pers_numbers': _("Nombre de personnes"),
                'room_count': _("Nombre de chambre"),
                'epis': _(u"Épis"),
                'heb_type': _(u"Type d'hébergement")}


class HebergementListingViewletManager(grok.ViewletManager):
    grok.name('gites.heblisting')

# register all viewlets in this viewlet manager:
grok.viewletmanager(HebergementListingViewletManager)
