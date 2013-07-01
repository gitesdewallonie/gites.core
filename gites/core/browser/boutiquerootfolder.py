# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from five import grok
from zope.interface import Interface
from gites.skin.interfaces import IBoutiqueRootFolder
from Products.CMFCore.utils import getToolByName

grok.context(Interface)
grok.templatedir('templates')


class BoutiqueRootFolder(grok.View):
    """
    View for the root of the boutique shop folder
    """
    grok.context(IBoutiqueRootFolder)
    grok.name('boutique_root')
    grok.require('zope2.View')

    def getBoutiqueItems(self):
        """
        Returns the list of Shop items available in the shop
        """
        cat = getToolByName(self.context, 'portal_catalog')
        shop = self.context
        url = '/'.join(shop.getPhysicalPath())
        contentFilter = {}
        path = {}
        path['query'] = url
        path['depth'] = 1
        contentFilter['path'] = path
        contentFilter['portal_type'] = ['BoutiqueItem']
        contentFilter['sort_on'] = 'effective'
        contentFilter['sort_order'] = 'reverse'
        results = cat.queryCatalog(contentFilter)
        results = list(results)
        return results
