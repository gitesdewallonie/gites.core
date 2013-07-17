# -*- coding: utf-8 -*-

from sqlalchemy import select, distinct
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from z3c.sqlalchemy import getSAWrapper
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from Products.Archetypes.interfaces import IVocabulary
from Products.Archetypes.atapi import DisplayList
from Products.CMFCore.utils import getToolByName
from zope.component import queryMultiAdapter
from plone.memoize import instance
from affinitic.db.cache import FromCache
from gites.db import session
from gites.db.content import Commune, Hebergement, Proprio

CARDS = ['carte01.jpg']


class CartesVocabulary(object):
    """
    Vocabulaire pour les cartes
    """
    implements(IVocabularyFactory)

    def __call__(self, context, name=None):
        """
        return the province vocabulary in the db
        """
        cartes = []
        for card in CARDS:
            term = SimpleTerm(value=card,
                              token=card,
                              title=card)
            cartes.append(term)
        return SimpleVocabulary(cartes)

CartesVocabularyFactory = CartesVocabulary()


class TypeHebVocabulary(object):
    """
    Vocabulaire pour la province
    """
    implements(IVocabularyFactory)

    def getTypes(self, context):
        request = context.REQUEST
        view = queryMultiAdapter((context, request),
                                 name="moteur_recherche_view")
        return view.getHebergementTypes()

    def __call__(self, context, name=None):
        """
        return the type heb vocabulary in the db
        """
        typeHebs = self.getTypes(context)
        typeHebs_items = []
        blankTerm = SimpleTerm(value=-1, token=-1, title=' ')
        typeHebs_items.append(blankTerm)
        for typeHeb in typeHebs:
            if typeHeb.get('pk') == 0:
                continue
            term = SimpleTerm(value=int(typeHeb.get('pk')),
                              token=int(typeHeb.get('pk')),
                              title=typeHeb.get('name'))
            typeHebs_items.append(term)
        return SimpleVocabulary(typeHebs_items)

TypeHebVocabularyFactory = TypeHebVocabulary()


class GroupedTypeHebVocabulary(TypeHebVocabulary):
    """
    Vocabulaire pour la province
    """
    implements(IVocabularyFactory)

    def getTypes(self, context):
        translation_service = getToolByName(context,
                                            'translation_service')

        utranslate = translation_service.utranslate
        request = context.REQUEST
        lang = request.get('LANGUAGE', 'en')
        return [{'pk': -2,
                 'name': utranslate('gites', "Gites et Meubles",
                                    context=context,
                                    target_language=lang,
                                    default="Gites")},
                {'pk': -3,
                 'name': utranslate('gites', "Chambre d'hote",
                                    context=context,
                                    target_language=lang,
                                    default="Chambre d'hote")}]

GroupedTypeHebVocabularyFactory = GroupedTypeHebVocabulary()


class ClassificationVocabulary(object):
    """
    Vocabulaire pour la classification (epis / cles)
    """
    implements(IVocabularyFactory)

    def __call__(self, context, name=None):
        """
        return the classification vocabulary
        """
        classification_items = []
        blankTerm = SimpleTerm(value=0, token=0, title=' ')
        classification_items.append(blankTerm)
        for value in xrange(1, 6):  # classification de 1 a 5
            term = SimpleTerm(value=value,
                              token=value,
                              title=str(value))
            classification_items.append(term)
        return SimpleVocabulary(classification_items)

ClassificationVocabularyFactory = ClassificationVocabulary()


class CriteriaVocabulary(object):
    """
    Vocabulaire Archetypes pour les critères
    """
    implements(IVocabulary)

    @instance.memoize
    def getDisplayList(self, instance):
        wrapper = getSAWrapper('gites_wallons')
        metadataTable = wrapper.getMapper('metadata')
        query = select([metadataTable.met_pk,
                        metadataTable.met_titre_fr],
                       metadataTable.met_filterable == True)
        query = query.order_by(metadataTable.met_titre_fr)
        results = query.execute().fetchall()
        criteria = [(str(r.met_pk), r.met_titre_fr) for r in results]
        return DisplayList(criteria)

CriteriaVocabularyFactory = CriteriaVocabulary()


class CitiesVocabulary(object):
    """
    Vocabulaire Archetypes pour les critères
    """
    implements(IVocabulary)

    def cities(self):
        query = session().query(distinct(Commune.com_nom).label('com_nom'))
        query = query.join('relatedHebergement', 'proprio')
        query = query.options(FromCache('gdw'))
        query = query.filter(Hebergement.heb_site_public == '1')
        query = query.filter(Proprio.pro_etat == True)
        return {city.com_nom for city in query.all()}

    def localities(self):
        query = session().query(distinct(Hebergement.heb_localite).label('heb_localite'))
        query = query.join('proprio')
        query = query.options(FromCache('gdw'))
        query = query.filter(Hebergement.heb_site_public == '1')
        query = query.filter(Proprio.pro_etat == True)
        return {heb.heb_localite for heb in query.all()}

    @instance.memoize
    def getDisplayList(self, instance):
        cities_localities_terms = [SimpleTerm(value=None, token=None, title=u'')]
        cities_localities = set()
        cities_localities = cities_localities.union(self.localities())
        cities_localities = cities_localities.union(self.cities())
        for city in sorted(cities_localities):
            term = SimpleTerm(value=city,
                              token=city.encode('ascii', 'ignore'),
                              title=city)
            cities_localities_terms.append(term)
        return SimpleVocabulary(cities_localities_terms)

CitiesVocabularyFactory = CitiesVocabulary()
