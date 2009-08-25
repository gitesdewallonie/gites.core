from Products.Five import BrowserView
from zope.interface import implements
from z3c.sqlalchemy import getSAWrapper
from gites.core.browser.interfaces import IDBReferenceWidgetView
from gites.core.adapters.interfaces import ITableSearch


class DBReferenceWidgetView(BrowserView):
    implements(IDBReferenceWidgetView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getSearchIndex(self, tableName):
        """
        Returns the available search index in the table
        """
        wrapper = getSAWrapper('gites_wallons')
        table = wrapper.getMapper(tableName)
        return ITableSearch(table()).searchableFields

    def searchItem(self, tableName, pk, uniqueColumn, prettyColumn):
        """
        Search for an element
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        table = wrapper.getMapper(tableName)
        column = getattr(table, uniqueColumn)
        result = session.query(table).filter(column==pk)
        if result:
            result = result[0]
            if not hasattr(result, prettyColumn):
                raise ValueError('%s not found in table %s' % (prettyColumn,
                                                            tableName))
            return getattr(result, prettyColumn)
        else:
            raise ValueError("Element not found or not unique: %s" % (pk))

    def search(self, tableName, columnName, searchTerm, resultColumns,
               exactMatch):
        """
        Returns the search results
        """
        wrapper = getSAWrapper('gites_wallons')
        table = wrapper.getMapper(tableName)
        tableSearch = ITableSearch(table())
        return tableSearch.search(wrapper, columnName,
                                  searchTerm, exactMatch)

    def safeTitle(self, title):
        """
        Escape invalid characters: '
        """
        return title.replace("'", "\\'")
