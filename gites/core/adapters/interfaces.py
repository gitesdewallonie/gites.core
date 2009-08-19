# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from zope.interface import Interface, Attribute


class ITableSearch(Interface):
    """
    Defines the search behaviour on a mapped table
    """

    searchableFields = Attribute('searchableFields',
                                 'A list of searchable fields in the table')
