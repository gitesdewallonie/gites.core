# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from Products.CMFCore.utils import getToolByName
from zope.interface import alsoProvides
from gites.core.interfaces import ISearch


def migrate(context):
    portal_url = getToolByName(context, 'portal_url')
    portal = portal_url.getPortalObject()
    portal.invokeFactory('Folder', id='search')
    searchFolder = getattr(portal, 'search')
    alsoProvides(searchFolder, ISearch)
