from zope.interface import implements
from gites.core.adapters.interfaces import ITableSearch


class RelationAwareSearch(object):

    def search(self, wrapper, column, searchTerm, exactMatch=False):
        """
        Return the search results
        """
        contextClass = self.context.__class__
        session = wrapper.session
        columnName = self.searchFieldMapper.get(column)
        column = getattr(contextClass, columnName, None)
        if column is not None:
            query = session.query(contextClass)
        else: # relation
            relation, columnName = columnName.split('.')
            mapper = wrapper.getMapper(relation)
            column = getattr(mapper, columnName)
            query = session.query(contextClass).join([relation])

        if exactMatch or searchTerm.isdigit():
            return query.filter(column==searchTerm)
        else:
            return query.filter(column.ilike("%%%s%%" % searchTerm))


class HebergementSearch(RelationAwareSearch):
    """
    Searching into the MaisonTourisme
    """
    implements(ITableSearch)

    searchableFields = ['Nom', 'PK']

    searchFieldMapper = {'Nom': 'heb_nom',
                         'PK': 'heb_pk'}

    def __init__(self, context):
        self.context = context


class MaisonTourismeSearch(RelationAwareSearch):
    """
    Searching into the MaisonTourisme
    """
    implements(ITableSearch)

    searchableFields = ['Commune', 'Nom']

    searchFieldMapper = {'Nom': 'mais_nom',
                         'Commune': 'commune.com_nom'}

    def __init__(self, context):
        self.context = context
