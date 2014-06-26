# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.viewlet.interfaces import IViewletManager


class IHebergementFolder(Interface):
    """
    Describe the folder containing all hebergement
    """


class IHebergementsFetcher(Interface):
    """
    Interface to fetch context/view related hebergements
    """

    def __call__():
        """
        return a list of hebergement
        """


class IMapRequest(IBrowserRequest):
    pass


class IMapViewletManager(IViewletManager):
    """
    """


class IHebergementInSearch(Interface):
    """ Marker interface for hebergement """


class IHebergementComparisonTable(Interface):
    """ Marker interface for the hosting comparison table """


class IHebergementComparisonThree(IHebergementComparisonTable):
    """ Marker interface for the comparison of three hostings """


class IHebergementComparisonFour(IHebergementComparisonThree):
    """ Marker interface for the comparison of four hostings """


class ISearch(Interface):
    """ Marker interface for search context """


class ITarifEditionTable(Interface):
    """ Marker interface for the tarif edition table """


class ITarifEditionManager(ITarifEditionTable):
    """ Marker interface for the tarif edition table to confirm """


class ITarifEditionToConfirm(ITarifEditionTable):
    """ Marker interface for the tarif edition table to confirm """


class ITarifToConfirmTable(Interface):
    """ Marker interface for the tarif to confirm table """
