# -*- coding: utf-8 -*-
from five import grok
from zope.interface import implements
from zope.component import getMultiAdapter
from .interfaces import IPackageView
from Products.CMFCore.utils import getToolByName

from gites.core.content.interfaces import IPackage
from gites.core.interfaces import IHebergementsFetcher

grok.templatedir('templates')


def getVignetteURL(context):
    """
    Return vignette URL for a package
    """
    cat = getToolByName(context, 'portal_catalog')
    path = '/'.join(context.getPhysicalPath())
    results = cat.searchResults(portal_type='Vignette',
                                path={'query': path})
    if results:
        return results[0].getURL()


class Package(grok.View):
    """
    View on Idee Sejour
    """
    implements(IPackageView)
    grok.context(IPackage)
    grok.name('package_view')
    grok.require('zope2.View')

    def getVignetteURL(self):
        return getVignetteURL(self.context)

    def getHebCount(self):
        """
        Return total number of herbegments in package
        """
        fetcher = getMultiAdapter((self.context, self,
                                  self.request),
                                  IHebergementsFetcher)
        return len(fetcher)
