# -*- coding: utf-8 -*-
from five import grok
from zope import interface, component
from gites.core.interfaces import IHebergementsFetcher
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
import random

grok.templatedir('templates')
grok.context(interface.Interface)


class OffresViewletManager(grok.ViewletManager):
    grok.name('gites.offres')

class IdeesSejours(grok.Viewlet):

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

    grok.viewletmanager(OffresViewletManager)

class DerniereMinute(grok.Viewlet):

    def _getValidDerniereMinute(self):
        """
        Retourne 1 derniere minute (non expiré) au hasard.
        """
        cat = getToolByName(self.context, 'portal_catalog')
        dateNow = DateTime()
        dateNow = DateTime(2012,1,1)
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

    def getRandomVignette(self, derniereMinuteUrl, amount=1):
        """
        Return a random vignette for a derniere minuet
        """
        cat = getToolByName(self.context, 'portal_catalog')
        results = cat.searchResults(portal_type='Vignette',
                                         path={'query': derniereMinuteUrl})
        results = list(results)
        random.shuffle(results)
        return results[:amount]

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

    grok.viewletmanager(OffresViewletManager)

class ChambreHotes(grok.Viewlet):

    grok.viewletmanager(OffresViewletManager)

class Boutique(grok.Viewlet):

    grok.viewletmanager(OffresViewletManager)

# register all viewlets in this viewlet manager:
grok.viewletmanager(OffresViewletManager)
