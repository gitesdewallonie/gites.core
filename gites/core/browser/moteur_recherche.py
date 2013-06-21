# -*- coding: utf-8 -*-

import zope.interface
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from z3c.sqlalchemy import getSAWrapper
from zope.component import getMultiAdapter
from gites.core.interfaces import IHebergementsFetcher, IMapRequest
from gites.core.utils import getGeocodedLocation


class MoteurRecherche(BrowserView):

    search_results = ViewPageTemplateFile('templates/search_results_hebergement.pt')

    def getBasicSearch(self):
        """
        Basic search
        """
        zope.interface.alsoProvides(self.request, IMapRequest)
        return self.search_results()

    def getHebergementByNameOrPk(self, reference):
        """
        Get the url of the hebergement by Pk or part of the name
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        hebTable = wrapper.getMapper('hebergement')
        try:
            int(reference)
        except ValueError:
            pass
        else:
            # we have a heb pk to search for
            hebergement = session.query(hebTable).get(reference)
            if hebergement and int(hebergement.heb_site_public) == 1 and hebergement.proprio.pro_etat:
               # L'hébergement doit être actif, ainsi que son propriétaire
                hebURL = getMultiAdapter((hebergement.__of__(self.context.hebergement), self.request), name="url")
                self.request.response.redirect(str(hebURL))
                return ''
            else:
                portal = getToolByName(self.context, 'portal_url').getPortalObject()
                return getMultiAdapter((portal, self.request),
                                       name="unknown_gites")()
        zope.interface.alsoProvides(self.request, IMapRequest)
        return self.search_results()

    def hebergementsCount(self):
        fetcher = getMultiAdapter((self.context, self, self.request),
                                  IHebergementsFetcher)
        return len(fetcher)

    def nearToNotFound(self):
        """
        Return near_to value if geolocalising search does not find it
        """
        near_to = self.request.form.get('nearTo')
        if near_to and not getGeocodedLocation(near_to):
            return near_to
        else:
            return None
