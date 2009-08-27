# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from Products.CMFCore.utils import getToolByName


def createPage(parentFolder, documentId, documentTitle):
    if documentId not in parentFolder.objectIds():
        parentFolder.invokeFactory('Document', documentId, title=documentTitle)
    document = getattr(parentFolder, documentId)
    #By default, created page are written in English
    #XXX bug here : document.setLanguage('en')
    publishObject(document)
    return document


def createFolder(parentFolder, folderId, folderTitle, excludeNav):
    if folderId not in parentFolder.objectIds():
        parentFolder.invokeFactory('Folder', folderId, title=folderTitle, excludeFromNav=excludeNav)
    createdFolder = getattr(parentFolder, folderId)
    createdFolder.reindexObject()
    createdFolder.exclude_from_nav=excludeNav
    createdFolder.reindexObject()
    publishObject(createdFolder)
    createdFolder.reindexObject()
    return createdFolder


def publishObject(obj):
    portal_workflow = getToolByName(obj, 'portal_workflow')
    if portal_workflow.getInfoFor(obj, 'review_state') in ['visible', 'private']:
        portal_workflow.doActionFor(obj, 'publish')
    return
