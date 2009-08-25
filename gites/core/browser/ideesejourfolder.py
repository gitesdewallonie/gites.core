# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
import random
from five import grok
from gites.core.content.interfaces import IIdeeSejourFolder
from Products.CMFCore.utils import getToolByName
from zope.interface import Interface

grok.context(Interface)
grok.templatedir('templates')


class IdeeSejourFolder(grok.View):
    """
    View on Idee Sejour folder
    """
    grok.context(IIdeeSejourFolder)
    grok.name('idee_sejour_folder')
    grok.require('zope2.View')

    def getRandomVignette(self, sejour_url, amount=1):
        """
        Return a random vignette for a sejour fute
        """
        cat = getToolByName(self.context, 'portal_catalog')
        results = cat.searchResults(portal_type='Vignette',
                                    path={'query': sejour_url})
        results = list(results)
        random.shuffle(results)
        return results[:amount]

    def getAvailableSejourInFolder(self):
        """
        Returns the list of IdeeSejour available in the current folder
        """
        cat = getToolByName(self.context, 'portal_catalog')
        idee_sejour_url = "/".join(self.context.getPhysicalPath())
        contentFilter = {}
        path = {}
        path['query'] = idee_sejour_url
        path['depth'] = 1
        contentFilter['path'] = path
        contentFilter['portal_type'] = ['IdeeSejourFolder', 'IdeeSejour']
        contentFilter['sort_on'] = 'getObjPositionInParent'
        contentFilter['review_state'] = 'published'
        results = cat.queryCatalog(contentFilter)
        results = [result.getObject() for result in results]
        return results
