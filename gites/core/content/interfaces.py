# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from zope.interface import Interface


class IPackage(Interface):
    """
    Package marker interface
    """


class IIdeeSejour(Interface):
    """
    Idee Sejour marker interface
    """


class IIdeeSejourFolder(Interface):
    """
    Idee Sejour Folder marker interface
    """


class IDerniereMinute(Interface):
    """
    Derniere Minute marker interface
    """


class ISejourFute(Interface):
    """
    Sejour Fute marker interface
    """


class IBoutiqueItem(Interface):
    """
    Boutique Item marker interface
    """
