# -*- coding: utf-8 -*-
from zope.container  import contained
from plone import api
from Products.CMFCore.utils import getToolByName
from gites.core.utils import clearPortlets


def migrate(context):
    portal_url = getToolByName(context, 'portal_url')
    portal = portal_url.getPortalObject()
    removePortlets(portal)
    removeContent(portal, 'couple')
    removeContent(portal, 'famille')
    removeContent(portal, 'groupe')
    removeContent(portal, 'societe')
    removeContent(portal, 'map')
    removeContent(portal, 'sejour-fute')
    removeContent(portal, 'best-deal')
    removeContent(portal, 'formation')
    removeContent(portal, 'gites-meubles')
    removeContent(portal, 'contacts')
    removeContent(portal, 'proposer-hebergement')
    removeContent(portal, 'decouvrir-wallonie')
    removeContent(portal, 'proposer-hebergement')
    removeContent(portal, 'decouvrir-wallonie')
    removeContent(portal, 'signaletiques')
    removeContent(portal, 'association')
    removeContent(portal, 'preparer-sejour')
    removeContent(portal, 'bnb')
    removeAllContentInsideFolder(portal, 'idee-sejour')
    catalog = getToolByName(context, 'portal_catalog')
    catalog.clearFindAndRebuild()


def removePortlets(portal):
    contained.fixing_up = True
    clearPortlets(portal)
    associationFolder = getattr(portal, 'association')
    clearPortlets(associationFolder)
    zoneMembreFolder = getattr(portal, 'zone-membre')
    clearPortlets(zoneMembreFolder)
    ideeSejourFolder = getattr(portal, 'idee-sejour')
    clearPortlets(ideeSejourFolder)
    contained.fixing_up = False


def removeAllContentInsideFolder(container, folderId):
    # no translations here
    folder = getattr(container, folderId, None)
    if not folder:
        return
    for objectId in folder.objectIds():
        if objectId:
            content = getattr(folder, objectId)
            api.content.delete(content)


def removeContent(folder, objectId):
    content = getattr(folder, objectId, None)
    if not content:
        return
    translations = content.getTranslations()
    for language in translations:
        translatedContent = translations[language][0]
        if translatedContent:
            api.content.delete(translatedContent)
