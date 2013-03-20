# -*- coding: utf-8 -*-
import random
from five import grok
from zope import interface
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime

grok.templatedir('templates')
grok.context(interface.Interface)


class OffresViewletManager(grok.ViewletManager):
    grok.name('gites.offres')


class IdeesSejours(grok.Viewlet):
    grok.order(10)

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

    def getRandomIdeesSejours(self):
        cat = getToolByName(self.context, 'portal_catalog')
        results = cat.searchResults(portal_type=['IdeeSejour'],
                                    review_state='published')
        results = list(results)
        random.shuffle(results)
        for sejour in results:
            if "%s/" % sejour.getURL() not in self.request.URL and \
               sejour.getURL() != self.request.URL:
                return sejour

    def getAllIdeesSejoursView(self):
        """
        Get the link to all the idees sejour
        """
        utool = getToolByName(self.context, 'portal_url')
        return '%s/idee-sejour' % utool()


class DerniereMinute(grok.Viewlet):
    grok.order(20)

    def _getValidDerniereMinute(self):
        """
        Retourne 1 derniere minute (non expiré) au hasard.
        """
        cat = getToolByName(self.context, 'portal_catalog')
        dateNow = DateTime()
        results = cat.searchResults(portal_type='DerniereMinute',
                                         end={'query': dateNow,
                                              'range': 'min'},
                                         review_state='published')
        results = list(results)
        random.shuffle(results)
        return results

    def getNiceEventStartDate(self, obj):
        startDate = obj.getEventStartDate()
        return startDate.strftime("%d-%m")

    def getNiceEventEndDate(self, obj):
        endDate = obj.getEventEndDate()
        return endDate.strftime("%d-%m")

    def getRandomDerniereMinute(self):
        """
        Retourne 1 derniere minute au hasard
        """
        results = self._getValidDerniereMinute()
        for derniereMinute in results:
            if "%s/" % derniereMinute.getURL() not in self.request.URL and derniereMinute.getURL() != self.request.URL:
                return derniereMinute.getObject()

    def getAllDerniereMinuteLink(self):
        """
        Get the link to all dernieres minutes
        """
        utool = getToolByName(self.context, 'portal_url')
        return '%s/dernieres-minutes' % utool()


class ChambreHotes(grok.Viewlet):
    grok.order(30)


class Boutique(grok.Viewlet):
    grok.order(40)

    def getRandomBoutiqueItem(self):
        """
        Get one random boutiqueItem
        """
        cat = getToolByName(self.context, 'portal_catalog')
        results = cat.searchResults(portal_type=['BoutiqueItem'],
                                    review_state='published')
        results = list(results)
        random.shuffle(results)
        for boutiqueItem in results:
            if "%s/" % boutiqueItem.getURL() not in self.request.URL and  boutiqueItem.getURL() != self.request.URL:
                return boutiqueItem.getObject()
        return None

    def getAllBoutiqueItemsView(self):
        """
        Get the link to all boutique items
        """
        utool = getToolByName(self.context, 'portal_url')
        return '%s/shop' % utool()


# register all viewlets in this viewlet manager:
grok.viewletmanager(OffresViewletManager)
