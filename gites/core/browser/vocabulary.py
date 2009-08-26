# -*- coding: utf-8 -*-

from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from z3c.sqlalchemy import getSAWrapper
from zope.interface import implements
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.component import queryMultiAdapter

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
            term= SimpleTerm(value=card,
                             token=card,
                             title=card)
            cartes.append(term)
        return SimpleVocabulary(cartes)

CartesVocabularyFactory = CartesVocabulary()


class ProvinceVocabulary(object):
    """
    Vocabulaire pour la province
    """
    implements(IVocabularyFactory)

    def __call__(self, context, name=None):
        """
        return the province vocabulary in the db
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        table = wrapper.getMapper('provinces')
        provinces = session.query(table).order_by(table.prov_nom)
        provinces_items = []
        blankTerm = SimpleTerm(value=-1, token=-1, title=' ')
        provinces_items.append(blankTerm)
        for province in provinces:
            term= SimpleTerm(value=int(province.prov_pk),
                             token=int(province.prov_pk),
                             title=province.prov_nom)
            provinces_items.append(term)
        return SimpleVocabulary(provinces_items)

ProvinceVocabularyFactory = ProvinceVocabulary()


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
            term= SimpleTerm(value=int(typeHeb.get('pk')),
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
        request = context.REQUEST
        view = queryMultiAdapter((context, request),
                                 name="moteur_recherche_view")
        return view.getGroupedHebergementTypes()

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
        blankTerm = SimpleTerm(value=-1, token=-1, title=' ')
        classification_items.append(blankTerm)
        for value in xrange(1, 5): #classification de 1 a 4
            term= SimpleTerm(value=value,
                             token=value,
                             title=str(value))
            classification_items.append(term)
        return SimpleVocabulary(classification_items)

ClassificationVocabularyFactory = ClassificationVocabulary()