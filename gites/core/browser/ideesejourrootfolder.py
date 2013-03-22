# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from five import grok
from Products.CMFCore.utils import getToolByName
from zope.interface import Interface
from gites.skin.interfaces import IIdeeSejourRootFolder

grok.context(Interface)
grok.templatedir('templates')


class IdeeSejourRootFolder(grok.View):
    """
    View on Idee Sejour folder
    """
    grok.context(IIdeeSejourRootFolder)
    grok.name('idee_sejour_root')
    grok.require('zope2.View')

    def getPackages(self):
        """
        Returns the list of Packages available in the current folder
        """
        cat = getToolByName(self.context, 'portal_catalog')
        ideeSejour = getattr(self.context, 'idee-sejour')
        url = '/'.join(ideeSejour.getPhysicalPath())
        contentFilter = {}
        path = {}
        path['query'] = url
        path['depth'] = 1
        contentFilter['path'] = path
        contentFilter['portal_type'] = ['Package']
        contentFilter['sort_on'] = 'getObjPositionInParent'
        contentFilter['review_state'] = 'published'
        results = cat.queryCatalog(contentFilter)
        results = list(results)
        return results

    def getVignette(self, packageUrl):
        """
        Return a vignette for the package
        """
        cat = getToolByName(self.context, 'portal_catalog')
        results = cat.searchResults(portal_type='Vignette',
                                    path={'query': packageUrl})
        if results:
            return results[0]
