# -*- coding: utf-8 -*-
from five import grok
from zope.interface import implements
from .interfaces import IPackageView
from Products.CMFCore.utils import getToolByName

from gites.core.content.interfaces import IPackage

grok.templatedir('templates')


class Package(grok.View):
    """
    View on Idee Sejour
    """
    implements(IPackageView)
    grok.context(IPackage)
    grok.name('package_view')
    grok.require('zope2.View')

    def getVignetteURL(self):
        """
        Return vignette URL for a package
        """
        cat = getToolByName(self.context, 'portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        results = cat.searchResults(portal_type='Vignette',
                                    path={'query': path})
        if results:
            return results[0].getURL()
