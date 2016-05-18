# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from zope.interface import Interface
from zope import schema
from gites.locales import GitesMessageFactory as _


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


class ISendToFormView(Interface):
    """
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

class ICommercialisationView(Interface):
    """
    View for the commercialisation of an hebergement
    """


class ITypeHebView(Interface):
    """
    Vue sur un type d hebergement
    """

    def typeHebergementName():
        """
        Get the hebergement type title translated
        """

    def getHebergements():
        """
        Return the concerned hebergements for the selected type of hebergement
        """


class ITypeHebCommuneView(Interface):
    """
    Vue sur un type d hebergement et une commune
    """

    def typeHebergementName():
        """
        Get the hebergement type title translated
        """

    def communeName():
        """
        Get the name of the commune
        """

    def getHebergements():
        """
        Return the concerned hebergements in this Town for the selected
        type of hebergement
        """


class IMoteurRecherche(Interface):

    def getBasicSearch():
        """
        Basic search
        """

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


class IPackageView(Interface):
    """
    view on a package
    """


class ISendMail(Interface):
    """
    Send Mail
    """

    def sendBlogSubscriptionMail():
        """
        envoi des informations d'inscription à la newsletter du blog
        """

    def sendMailToProprio():
        """
        Envoi un mail au proprio via le site
        """

    def sendMailForProblem():
        """
        Envoi un mail pour signaler un problème
        """


class ISearchHebergement(Interface):
    """
    A search module to search hebergement
    """

    hebergementType = schema.Choice(
        title=_("Hebergement Type"),
        description=_("Select a type of Hebergement"),
        required=True,
        vocabulary="gitescontent.groupedtypehebergement")

    classification = schema.Choice(
        title=_('Classification'),
        description=_("Select a classification"),
        required=False,
        vocabulary="gitescontent.classification")

    capacityMin = schema.Int(
        title=_('Minimum Capacity'),
        description=_('The minimum capacity of your hebergement'),
        required=False)

    roomAmount = schema.Int(
        title=_('Number of rooms'),
        description=_('The number of rooms in hebergement'),
        required=False)

    animals = schema.Bool(
        title=_('Animals authorized'),
        description=_('Are animals authorized in the Hebergement'),
        required=False)

    smokers = schema.Bool(
        title=_('Smoking allowed'),
        description=_('Are people allowed to smoke in the Hebergement'),
        required=False)

    fromDate = schema.Date(title=_('Stay from'),
                           description=_('Stay from'),
                           required=False)

    toDate = schema.Date(title=_('Stay to'),
                         description=_('Stay to'),
                         required=False)


class IBasicSearchHebergement(ISearchHebergement):
    """
    A basic search module to search hebergement
    """


class IBasicSearchHebergementTooMuch(ISearchHebergement):
    """
    A basic search module to search hebergement
    """


class ISearchHebergementTooMuch(ISearchHebergement):
    """
    A search module to search hebergement
    """


class ISearchHosting(Interface):

    hebergementType = schema.Choice(
        title=_("Hebergement Type"),
        required=False,
        vocabulary="gitescontent.groupedtypehebergement")

    classification = schema.Choice(
        title=_('Classification'),
        required=False,
        vocabulary="gitescontent.classification")

    capacityMin = schema.Int(
        title=_('Minimum Capacity'),
        required=False)

    roomAmount = schema.Int(
        title=_('Number of rooms'),
        required=False)

    animals = schema.Bool(
        title=_('Animals authorized'),
        required=False)

    smokers = schema.Bool(
        title=_('Smoking allowed'),
        required=False)

    fromDate = schema.Date(
        title=_(u'Stay from'),
        required=False)

    toDate = schema.Date(
        title=_(u'Stay to'),
        required=False)

    fromDateAvancee = schema.Date(
        title=_(u'Stay from'),
        required=False)

    toDateAvancee = schema.Date(
        title=_(u'Stay to'),
        required=False)

    nearTo = schema.TextLine(
        title=_('Near to'),
        required=False)
