# -*- coding: utf-8 -*-

from sqlalchemy import select
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from z3c.sqlalchemy import getSAWrapper
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from Products.Archetypes.interfaces import IVocabulary
from Products.Archetypes.atapi import DisplayList
from Products.CMFCore.utils import getToolByName
from zope.component import queryMultiAdapter
from plone.memoize import forever

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

    @forever.memoize
    def getDisplayList(self, instance):
        wrapper = getSAWrapper('gites_wallons')
        communeTable = wrapper.getMapper('commune')
        hebergementTable = wrapper.getMapper('hebergement')
        query = select([communeTable.com_nom,
                        communeTable.com_pk],
                       distinct=communeTable.com_nom)
        query.append_whereclause(hebergementTable.heb_com_fk == communeTable.com_pk)
        query = query.order_by(communeTable.com_nom)
        cities = [SimpleTerm(value=None, token=None, title=u'')]
        for city in query.execute().fetchall():
            term = SimpleTerm(value=city.com_pk,
                              token=city.com_pk,
                              title=city.com_nom)
            cities.append(term)
        return SimpleVocabulary(cities)

CitiesVocabularyFactory = CitiesVocabulary()
