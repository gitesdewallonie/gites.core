# -*- coding: utf-8 -*-
from five import grok
from zope import interface, component
from gites.core.interfaces import IHebergementsFetcher


grok.templatedir('templates')
grok.context(interface.Interface)


class HebergementsInListing(grok.Viewlet):

    def hebergements(self):
        fetcher = component.getMultiAdapter((self.context, self.view,
                                             self.request),
                                            IHebergementsFetcher)
        return fetcher()


class HebergementListingViewletManager(grok.ViewletManager):
    grok.name('gites.heblisting')

# register all viewlets in this viewlet manager:
grok.viewletmanager(HebergementListingViewletManager)
