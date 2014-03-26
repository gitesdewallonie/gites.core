# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from Products.CMFCore.utils import getToolByName
from gites.core.utils import publishObject


def migrate(context):
    portal_url = getToolByName(context, 'portal_url')
    portal = portal_url.getPortalObject()
    portal.invokeFactory('Folder', id='carousel', title='Carousel')
    carouselFolder = getattr(portal, 'carousel')
    publishObject(carouselFolder)
    carouselFolder.setLanguage('')
    carouselFolder.setConstrainTypesMode(1)
    carouselFolder.setLocallyAllowedTypes(['Document', 'Image', 'Link'])
    carouselFolder.setImmediatelyAddableTypes(['Document', 'Image', 'Link'])
    carouselFolder.reindexObject()
