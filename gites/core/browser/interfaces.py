# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from zope.interface import Interface


class IDBReferenceWidgetView(Interface):

    def getSearchIndex(tableName):
        """
        Return the available search index in the table
        """

    def search(tableName, columnName, searchTerm, resultColumns):
        """
        Returns the search results
        """

    def searchItem(tableName, pk, uniqueColumn, prettyColumn):
        """
        Search for an element
        """

    def safeTitle(title):
        """
        Escape invalid characters: '
        """
