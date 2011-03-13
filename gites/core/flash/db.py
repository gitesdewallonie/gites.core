# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from Products.Five import BrowserView
from z3c.sqlalchemy import getSAWrapper
from sqlalchemy import select
from zope.component import queryMultiAdapter
from plone.memoize import forever


class FlashGitesView(BrowserView):

    def _adaptsSAResults(self, results):
        items = []
        for result in results:
            heb = dict()
            for columnName, value in result.items():
                heb[columnName] = value
            items.append(heb)
        return items

    @forever.memoize
    def getMaisonsDuTourisme(self):
        wrapper = getSAWrapper('gites_wallons')
        MaisonTouristique = wrapper.getMapper('maison_tourisme')
        query = select([MaisonTouristique.mais_nom,
                        MaisonTouristique.mais_url,
                        MaisonTouristique.mais_code,
                        MaisonTouristique.mais_gps_long,
                        MaisonTouristique.mais_gps_lat,
                        MaisonTouristique.mais_id])
        return self._adaptsSAResults(query.execute().fetchall())

    @forever.memoize
    def getInfosTouristiques(self):
        wrapper = getSAWrapper('gites_wallons')
        InfoTouristique = wrapper.getMapper('info_touristique')
        TypeInfoTouristique = wrapper.getMapper('type_info_touristique')
        query = select([InfoTouristique.infotour_nom,
                        InfoTouristique.infotour_url,
                        InfoTouristique.infotour_gps_long,
                        InfoTouristique.infotour_gps_lat,
                        TypeInfoTouristique.typinfotour_nom_fr,
                        InfoTouristique.infotour_localite])
        query.append_whereclause(TypeInfoTouristique.typinfotour_pk==InfoTouristique.infotour_type_infotour_fk)
        return self._adaptsSAResults(query.execute().fetchall())

    @forever.memoize
    def getInfosPratiques(self):
        wrapper = getSAWrapper('gites_wallons')
        InfoPratique = wrapper.getMapper('info_pratique')
        TypeInfoPratique = wrapper.getMapper('type_info_pratique')
        query = select([InfoPratique.infoprat_nom,
                        InfoPratique.infoprat_url,
                        InfoPratique.infoprat_gps_long,
                        InfoPratique.infoprat_gps_lat,
                        TypeInfoPratique.typinfoprat_nom_fr,
                        InfoPratique.infoprat_localite])
        query.append_whereclause(InfoPratique.infoprat_type_infoprat_fk==TypeInfoPratique.typinfoprat_pk)
        return self._adaptsSAResults(query.execute().fetchall())

    @forever.memoize
    def getHebergements(self):
        wrapper = getSAWrapper('gites_wallons')
        Hebergement = wrapper.getMapper('hebergement')
        TypeHebergement =wrapper.getMapper('type_heb')
        Proprio = wrapper.getMapper('proprio')
        query = select([Hebergement.heb_pk,
                        TypeHebergement.type_heb_code,
                        TypeHebergement.type_heb_nom,
                        Hebergement.heb_gps_long,
                        Hebergement.heb_gps_lat,
                        Hebergement.heb_cgt_cap_max,
                        Hebergement.heb_localite,
                        Hebergement.heb_cgt_cap_min,
                        Hebergement.heb_nom])
        query.append_whereclause(TypeHebergement.type_heb_pk==Hebergement.heb_typeheb_fk)
        query.append_whereclause(Hebergement.heb_site_public == '1')
        query.append_whereclause(Proprio.pro_pk==Hebergement.heb_pro_fk)
        query.append_whereclause(Proprio.pro_etat == True)
        return self._adaptsSAResults(query.execute().fetchall())

    @forever.memoize
    def getHebergementUrl(self, heb_pk):
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        Hebergement = wrapper.getMapper('hebergement')
        hebergement = session.query(Hebergement).get(heb_pk)
        hebergementURL = queryMultiAdapter((hebergement.__of__(self.context.hebergement), self.context.REQUEST),
                                           name='url')
        return hebergementURL()
