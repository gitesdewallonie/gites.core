# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from Products.CMFCore.utils import getToolByName
from zope.interface import alsoProvides
from gites.skin.interfaces import IDerniereMinuteRootFolder


def migrate(context):
    portal_url = getToolByName(context, 'portal_url')
    portal = portal_url.getPortalObject()
    derniereMinutes = getattr(portal, 'dernieres-minutes')
    alsoProvides(derniereMinutes, IDerniereMinuteRootFolder)
