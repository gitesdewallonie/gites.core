# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from Products.CMFCore.utils import getToolByName
from Products.CMFPlacefulWorkflow.PlacefulWorkflowTool import WorkflowPolicyConfig_id
import logging
from gites.core.utils import createFolder
logger = logging.getLogger('gites.core')


def setupgites(context):
    if context.readDataFile('gites.core_various.txt') is None:
        return
    logger.debug('Setup gites core')
    portal = context.getSite()
    createFolder(portal, "zone-membre", "Zone Membre", True)
    createFolder(portal, "idee-sejour", "Idee sejour", True)
    setupProprioPlacefulWorkflow(portal)


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
