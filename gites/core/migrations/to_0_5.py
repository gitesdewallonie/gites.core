# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from Products.CMFCore.utils import getToolByName
from zope.interface import alsoProvides
from gites.skin.interfaces import IBoutiqueRootFolder


def migrate(context):
    portal_url = getToolByName(context, 'portal_url')
    portal = portal_url.getPortalObject()
    shopFolder = getattr(portal, 'shop')
    alsoProvides(shopFolder, IBoutiqueRootFolder)
