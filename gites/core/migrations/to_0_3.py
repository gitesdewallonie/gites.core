# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName


def migrate(context):
    portal_url = getToolByName(context, 'portal_url')
    portal = portal_url.getPortalObject()

    ideesSejourFolder = getattr(portal, "idee-sejour")
    ideesSejourFolder.setLocallyAllowedTypes(['Package'])
    ideesSejourFolder.setImmediatelyAddableTypes(['Package'])
    ideesSejourFolder.reindexObject()
