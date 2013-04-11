# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName


def migrate(context):
    portal_url = getToolByName(context, 'portal_url')
    portal = portal_url.getPortalObject()

    ideesSejourFolder = getattr(portal, 'idee-sejour')
    ideesSejourFolder.setConstrainTypesMode(1)
    ideesSejourFolder.setLocallyAllowedTypes(['Package'])
    ideesSejourFolder.setImmediatelyAddableTypes(['Package'])
    ideesSejourFolder.reindexObject()

    shopFolder = getattr(portal, 'shop')
    shopFolder.setConstrainTypesMode(1)
    shopFolder.setLocallyAllowedTypes(['BoutiqueItem'])
    shopFolder.setImmediatelyAddableTypes(['BoutiqueItem'])
    shopFolder.reindexObject()

    derniereMinutes = getattr(portal, 'dernieres-minutes')
    derniereMinutes.setConstrainTypesMode(1)
    derniereMinutes.setLocallyAllowedTypes(['DerniereMinute'])
    derniereMinutes.setImmediatelyAddableTypes(['DerniereMinute'])
