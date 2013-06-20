# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
import logging
import tempfile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlacefulWorkflow.PlacefulWorkflowTool import WorkflowPolicyConfig_id
from Products.LocalFS.LocalFS import manage_addLocalFS
from gites.core.utils import createFolder
logger = logging.getLogger('gites.core')


def setupgites(context):
    if context.readDataFile('gites.core_various.txt') is None:
        return
    logger.debug('Setup gites core')
    portal = context.getSite()
    createFolder(portal, "zone-membre", "Zone Membre", True)
#    setupProprioPlacefulWorkflow(portal)
    disableGlobalAddingForContentType(portal, 'GeoLocation')
    createLocalFS(portal)
    if not hasattr(portal, 'idee-sejour'):
        createFolder(portal, "idee-sejour", "Idee sejour", True)
    ideesSejourFolder = getattr(portal, 'idee-sejour')
    changeFolderView(portal, ideesSejourFolder, 'idee_sejour_root')


def createLocalFS(portal):
    if 'photos_heb_tmp' not in portal.objectIds():
        manage_addLocalFS(portal, 'photos_heb_tmp', 'Photos heb temporaires',
                          tempfile.gettempdir())
    if 'photos_proprio' not in portal.objectIds():
        manage_addLocalFS(portal, 'photos_proprio', 'Photos proprio',
                          tempfile.gettempdir())
    if 'photos_proprio_tmp' not in portal.objectIds():
        manage_addLocalFS(portal, 'photos_proprio_tmp', 'Photos proprio temporaires',
                          tempfile.gettempdir())


def addViewToType(portal, typename, templatename):
    pt = getToolByName(portal, 'portal_types')
    foldertype = getattr(pt, typename)
    available_views = list(foldertype.getAvailableViewMethods(portal))
    if not templatename in available_views:
        available_views.append(templatename)
        foldertype.manage_changeProperties(view_methods=available_views)


def changeFolderView(portal, folder, viewname):
    addViewToType(portal, 'Folder', viewname)
    if folder.getLayout() != viewname:
        folder.setLayout(viewname)


def disableGlobalAddingForContentType(portal, contentTypeName):
    portal_types = portal.portal_types
    contentType = portal_types[contentTypeName]
    contentType.global_allow = False


def setupProprioPlacefulWorkflow(portal):
    placefulWorkflow = getToolByName(portal, 'portal_placeful_workflow')
    if not hasattr(placefulWorkflow, 'proprio_policy'):
        placefulWorkflow.manage_addWorkflowPolicy('proprio_policy',
                                                  'default_workflow_policy (Simple Policy)')
    zoneMembreFolder = getattr(portal, 'zone-membre')
    policy = placefulWorkflow.getWorkflowPolicyById('proprio_policy')
    policy.setChainForPortalTypes(zoneMembreFolder.getLocallyAllowedTypes(),
                                  ['intranet_workflow'])
    policy.setChainForPortalTypes(['Document'], ['intranet_workflow'])
    policy.setChainForPortalTypes(['Event'], ['intranet_workflow'])
    policy.setChainForPortalTypes(['News Item'], ['intranet_workflow'])
    policy.setChainForPortalTypes(['File'], ['intranet_workflow'])
    policy.setChainForPortalTypes(['Image'], ['intranet_workflow'])
    policy.setChainForPortalTypes(['Folder'], ['intranet_folder_workflow'])
    policy.setDefaultChain(['intranet_workflow'])
    zoneMembreFolderPolicy = getattr(zoneMembreFolder, WorkflowPolicyConfig_id, None)
    if zoneMembreFolderPolicy is None:
        zoneMembreFolder.manage_addProduct['CMFPlacefulWorkflow'].manage_addWorkflowPolicyConfig()
        zoneMembrePolicy = getattr(zoneMembreFolder, WorkflowPolicyConfig_id)
        zoneMembrePolicy.setPolicyBelow('proprio_policy')
        zoneMembrePolicy.setPolicyIn('proprio_policy')
    zoneMembreFolder.reindexObjectSecurity()
