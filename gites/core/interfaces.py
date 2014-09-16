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
from z3c.table.interfaces import IValues


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


class ITarifTable(Interface):
    """ Marker interface for the tarif table """


class ITarifDisplayTable(ITarifTable):
    """ Marker interface for the tarif display table """


class ITarifDisplayType(ITarifTable):
    """ Marker interface for the tarif type column display """


class ITarifDisplaySubtype(ITarifTable):
    """ Marker interface for the tarif type column display """


class ITarifEditionTable(ITarifTable):
    """ Marker interface for the tarif edition table """


class ITarifEditionManager(ITarifEditionTable):
    """ Marker interface for the tarif edition table for manager """


class ITarifEditionProprio(ITarifEditionTable):
    """ Marker interface for the tarif edition table for proprio """


class ITarifToConfirmTable(Interface):
    """ Marker interface for the tarif to confirm table """


class IValuesSeason(IValues):
    """
    Season section table values marker interface
    """


class IValuesWeek(IValues):
    """
    Week section table values marker interface
    """


class IValuesWeekend(IValues):
    """
    Weekend section table values marker interface
    """


class IValuesRoom(IValues):
    """
    Room section table values marker interface
    """


class IValuesChristmas(IValues):
    """
    Christmas section table values marker interface
    """


class IValuesCharges(IValues):
    """
    Charges section table values marker interface
    """


class IValuesOther(IValues):
    """
    Other section table values marker interface
    """
