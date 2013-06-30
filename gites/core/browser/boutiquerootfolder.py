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
from sqlalchemy import desc
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
import random
from z3c.sqlalchemy import getSAWrapper

grok.context(Interface)
grok.templatedir('templates')


class BoutiqueRootFolder(grok.View):
    """
    View for the root of the boutique shop folder
    """
    grok.context(IBoutiqueRootFolder)
    grok.name('boutique_root_folder')
    grok.require('zope2.View')

    def __init__(self, context, request, *args, **kw):
        super(BoutiqueRootFolder, self).__init__(context, request, *args, **kw)
        self.cat = getToolByName(self.context, 'portal_catalog')
        utool = getToolByName(context, 'portal_url')
        self.portal_url = utool()

    def _getValidBoutiques(self):
        results = self.cat.searchResults(portal_type='shop',
                                               end={'query': DateTime(),
                                                    'range': 'min'},
                                               review_state='published')
        results = list(results)
        random.shuffle(results)
        return results

    def getNiceEventStartDate(self):
        """
        """
        startDate = self.context.getEventStartDate()
        return startDate.strftime("%d-%m")

    def getNiceEventEndDate(self):
        endDate = self.context.getEventEndDate()
        return endDate.strftime("%d-%m")
