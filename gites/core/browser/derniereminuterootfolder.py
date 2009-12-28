# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from five import grok
from zope.interface import Interface
from gites.skin.interfaces import IDerniereMinuteRootFolder
from sqlalchemy import desc
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
import random
from z3c.sqlalchemy import getSAWrapper

grok.context(Interface)
grok.templatedir('templates')


class DerniereMinuteRootFolder(grok.View):
    """
    View for the root of the derniere minute folder
    """
    grok.context(IDerniereMinuteRootFolder)
    grok.name('derniere_minute_root_folder')
    grok.require('zope2.View')

    def __init__(self, context, request, *args, **kw):
        super(DerniereMinuteRootFolder, self).__init__(context, request, *args, **kw)
        self.cat = getToolByName(self.context, 'portal_catalog')
        utool = getToolByName(context, 'portal_url')
        self.portal_url = utool()

    def _getValidDernieresMinutes(self):
        results = self.cat.searchResults(portal_type='DerniereMinute',
                                               end={'query': DateTime(),
                                                    'range': 'min'},
                                               review_state='published')
        results = list(results)
        random.shuffle(results)
        return results

    def getLastPromotions(self):
        results = self._getValidDernieresMinutes()
        validPromotions = []
        for promotionBrain in results:
            promotion = promotionBrain.getObject()
            if promotion.getCategory() == 'promotion':
                validPromotions.append(promotion)
        return validPromotions

    def getLastDernieresMinutes(self):
        results = self._getValidDernieresMinutes()
        validLastMinut = []
        for lastMinutBrain in results:
            lastMinut = lastMinutBrain.getObject()
            if lastMinut.getCategory() == 'derniere-minute':
                validLastMinut.append(lastMinut)
        return validLastMinut

    def getLastHebergements(self):
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        Hebergement = wrapper.getMapper('hebergement')
        query = session.query(Hebergement)
        query = query.filter(Hebergement.heb_etat == '1')
        query = query.order_by(desc(Hebergement.heb_pk))
        query = query.limit(10)
        results = [hebergement.__of__(self.context.hebergement) for hebergement in query.all()]
        return results

    def getNiceEventStartDate(self):
        """
        """
        startDate = self.context.getEventStartDate()
        return startDate.strftime("%d-%m")

    def getNiceEventEndDate(self):
        endDate = self.context.getEventEndDate()
        return endDate.strftime("%d-%m")
