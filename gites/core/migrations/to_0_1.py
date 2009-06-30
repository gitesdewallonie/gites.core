# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
import logging

from zope.interface import implementedBy
from zope.interface import directlyProvides
from zope.interface import directlyProvidedBy


from Products.CMFCore.utils import getToolByName
from gites.core.content.hebergementfolder import HebergementFolder

BASE = {'HebergementFolder': HebergementFolder}
TYPES_TO_MIGRATE = BASE.keys()


def migrateTypes(site):
    """call migrateType for all types where we want to have a new base"""
    for typename in BASE.keys():
        log = logging.getLogger('migrateGites')
        log.info('Migrate %s : begin' % typename)
        migrateType(site, typename)
        log.info('Migrate %s : end' % typename)


def migrateType(portal, typename):
    """
    remove references to previous objects
    """
    ct = getToolByName(portal, 'portal_catalog')
    objects = [b.getObject() for b in ct(portal_type=typename)]
    for object in objects:
        oldInterfaces = directlyProvidedBy(object)
        oldClass = object.__class__
        # change base class
        newClass = BASE[typename]
        object.__class__ = newClass
        # fix interfaces
        oldImplement = implementedBy(oldClass)
        newImplement = implementedBy(newClass)
        newInterfaces = oldInterfaces - oldImplement + newImplement
        directlyProvides(object, newInterfaces)
        object._p_changed = 1


def migrate(context):
    portal_url = getToolByName(context, 'portal_url')
    portal = portal_url.getPortalObject()
    migrateTypes(portal)
