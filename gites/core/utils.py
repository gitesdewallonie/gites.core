# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from affinitic.pwmanager.interfaces import IPasswordManager
from hashlib import md5
from plone.memoize import forever
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.app.portlets.portlets import classic
from zope.component import getMultiAdapter
from pygeocoder import Geocoder
from pygeolib import GeocoderError


def createPage(parentFolder, documentId, documentTitle, excludeNav=False):
    if documentId not in parentFolder.objectIds():
        parentFolder.invokeFactory('Document', documentId, title=documentTitle)
    document = getattr(parentFolder, documentId)
    document.exclude_from_nav = excludeNav
    publishObject(document)
    return document


def createFolder(parentFolder, folderId, folderTitle, excludeNav):
    if folderId not in parentFolder.objectIds():
        parentFolder.invokeFactory('Folder', folderId, title=folderTitle, excludeFromNav=excludeNav)
    createdFolder = getattr(parentFolder, folderId)
    createdFolder.reindexObject()
    createdFolder.exclude_from_nav = excludeNav
    createdFolder.reindexObject()
    publishObject(createdFolder)
    createdFolder.reindexObject()
    return createdFolder


def publishObject(obj):
    portal_workflow = getToolByName(obj, 'portal_workflow')
    if portal_workflow.getInfoFor(obj, 'review_state') in ['visible', 'private']:
        portal_workflow.doActionFor(obj, 'publish')
    return


def setupClassicPortlet(folder, template, column):
    #Add classic portlet (using template) to folder
    manager = getManager(folder, column)
    assignments = getMultiAdapter((folder, manager), IPortletAssignmentMapping)

    assignment = classic.Assignment(template=template, macro='portlet')
    if template in assignments:
        del assignments[template]
    assignments[template] = assignment


def getManager(folder, column):
    if column == 'left':
        manager = getUtility(IPortletManager, name=u'plone.leftcolumn', context=folder)
    else:
        manager = getUtility(IPortletManager, name=u'plone.rightcolumn', context=folder)
    return manager


def clearColumnPortlets(folder, column):
    manager = getManager(folder, column)
    assignments = getMultiAdapter((folder, manager), IPortletAssignmentMapping)
    for portlet in assignments:
        del assignments[portlet]


def clearPortlets(folder):
    clearColumnPortlets(folder, 'left')
    clearColumnPortlets(folder, 'right')


def changeDocumentView(document, viewname):
    if document.getLayout() != viewname:
        document.setLayout(viewname)


def changeFolderView(portal, folder, viewname):
    addViewToType(portal, 'Folder', viewname)
    if folder.getLayout() != viewname:
        folder.setLayout(viewname)


def addViewToType(portal, typename, templatename):
    pt = getToolByName(portal, 'portal_types')
    foldertype = getattr(pt, typename)
    available_views = list(foldertype.getAvailableViewMethods(portal))
    if not templatename in available_views:
        available_views.append(templatename)
        foldertype.manage_changeProperties(view_methods=available_views)


@forever.memoize
def getGeocodedLocation(location, language='en'):
    if location is None:
        return None
    try:
        google_api = getUtility(IPasswordManager, 'googleapi')
        geocoder = Geocoder(api_key=google_api.password)
        locations = geocoder.geocode(location,
                                     region='be',
                                     language=language)
    except GeocoderError, e:
        if e.status == u'ZERO_RESULTS':
            return None
        else:
            raise e
    return locations[0]


def calculate_md5(value):
    return md5('%s%s' % (value, get_md5_salt())).hexdigest()


@forever.memoize
def get_md5_salt():
    pw_manager = getUtility(IPasswordManager, 'md5')
    return pw_manager.getLoginPassWithSeparator('')
