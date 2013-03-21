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


class IHebergementView(Interface):
    """
    View for the full description of an hebergement
    """

    def redirectInactive():
        """
        Redirect if gites / proprio is not active
        """

    def getTypeHebergement():
        """
        Get the hebergement type title translated
        """

    def getHebergementSituation():
        """
        Get the hebergement type title translated
        """

    def getHebergementDescription():
        """
        Get the hebergement type title translated
        """

    def getHebergementDistribution():
        """
        Get the hebergement type title translated
        """

    def getHebergementSeminaireVert():
        """
        Get the hebergement seminaire vert information translated
        """

    def getHebergementCharge():
        """
        Get the hebergement type title translated
        """

    def getTypeHebInCommuneURL():
        """
        Get the commune and type hebergement URL
        """

    def getRelatedSejourFute():
        """
        Get Sejour Fute related to this hebergement
        """


class IHebergementIconsView(Interface):
    """
        View for the icons of an hebergement
    """

    def getEpis():
        """
        Get the epis icons
        """

    def getSignaletiqueUrl():
        """
        return the url of the signaletique
        """


class IMoteurRecherche(Interface):

    def getHebergementByNameOrPk(reference):
        """
        Get the url of the hebergement by Pk or part of the name
        """

    def getHebergementTypes():
        """
        retourne les types d hebergements
        """

    def getGroupedHebergementTypes():
        """
        retourne les deux groupes de types d hebergements
        """
