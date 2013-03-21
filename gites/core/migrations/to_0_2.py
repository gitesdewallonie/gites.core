# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from gites.core.utils import clearPortlets


def migrate(context):
    portal_url = getToolByName(context, 'portal_url')
    portal = portal_url.getPortalObject()
    clearPortlets(portal)
