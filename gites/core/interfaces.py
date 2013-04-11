# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from zope.interface import Interface
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

class IMapViewletManager(IViewletManager):
    """
    """
