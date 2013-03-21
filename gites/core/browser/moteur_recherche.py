# -*- coding: utf-8 -*-

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from z3c.sqlalchemy import getSAWrapper
from zope.component import queryMultiAdapter


class MoteurRecherche(BrowserView):

    search_results = ViewPageTemplateFile('templates/search_results_hebergement.pt')

    def getHebergementByNameOrPk(self, reference):
        """
        Get the url of the hebergement by Pk or part of the name
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        hebTable = wrapper.getMapper('hebergement')
        proprioTable = wrapper.getMapper('proprio')
        try:
            int(reference)
        except ValueError:
            # we have a heb name to search for
            query = session.query(hebTable).join('proprio')
            query = query.filter(hebTable.heb_site_public == '1')
            query = query.filter(proprioTable.pro_etat == True)
            query = query.filter(hebTable.heb_nom.ilike("%%%s%%" % reference))
            query = query.order_by(hebTable.heb_nom)
            query = query.limit(100)  # performance matters
            self.selectedHebergements = [hebergement.__of__(self.context.hebergement) for hebergement in query.all()]
            if len(self.selectedHebergements) == 1:
                hebURL = queryMultiAdapter((self.selectedHebergements[0], self.request),
                                           name="url")
                self.request.response.redirect(str(hebURL))
                return ''
            return self.search_results()
        else:
            # we have a heb pk to search for
            hebergement = session.query(hebTable).get(reference)
            if hebergement and \
               int(hebergement.heb_site_public) == 1 and \
               hebergement.proprio.pro_etat:
               # L'hébergement doit être actif, ainsi que son propriétaire
                hebURL = queryMultiAdapter((hebergement.__of__(self.context.hebergement), self.request), name="url")
                self.request.response.redirect(str(hebURL))
                return ''
            else:
                portal = getToolByName(self.context, 'portal_url').getPortalObject()
                return queryMultiAdapter((portal, self.request),
                                           name="unknown_gites")()

    def getGroupedHebergementTypes(self):
        """
        retourne les deux groupes de types d'hebergements
        """
        # get some translation interfaces
        translation_service = getToolByName(self.context,
                                            'translation_service')

        utranslate = translation_service.utranslate
        lang = self.request.get('LANGUAGE', 'en')
        return [{'pk': -2,
                 'name': utranslate('gites', "Gites et Meubles",
                                    context=self.context,
                                    target_language=lang,
                                    default="Gites")},
                {'pk': -3,
                 'name': utranslate('gites', "Chambre d'hote",
                                    context=self.context,
                                    target_language=lang,
                                    default="Chambre d'hote")}]

    def getHebergementTypes(self):
        """
        retourne les types d hebergements
        table type_heb
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        TypeHeb = wrapper.getMapper('type_heb')
        results = session.query(TypeHeb).all()
        language = self.request.get('LANGUAGE', 'en')
        typesList = []
        for typeHeb in results:
            types = {}
            types['pk'] = typeHeb.type_heb_pk
            types['name'] = typeHeb.getTitle(language)
            typesList.append(types)
        return typesList
