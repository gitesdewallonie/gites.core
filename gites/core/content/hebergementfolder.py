# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import Schema, BaseSchema, registerType
from gites.core.config import PROJECTNAME
from Products.ATContentTypes.content.folder import ATFolder
from zope.interface import implements
from gites.core.interfaces import IHebergementFolder
from Products.CMFCore.utils import getToolByName
from z3c.sqlalchemy import getSAWrapper
from persistent.dict import PersistentDict

schema = Schema((

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

HebergementFolder_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
HebergementFolder_schema = ATFolder.schema.copy() + \
    schema.copy()
##/code-section after-schema

class HebergementFolder(ATFolder):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(ATFolder, '__implements__', ()))

    # This name appears in the 'add' box
    archetype_name = 'HebergementFolder'

    meta_type = 'HebergementFolder'
    portal_type = 'HebergementFolder'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 1
    #content_icon = 'HebergementFolder.gif'
    immediate_view = 'view'
    default_view = 'view'
    suppl_views = ()
    typeDescription = "HebergementFolder"
    typeDescMsgId = 'description_edit_hebergementfolder'

    _at_rename_after_creation = True

    schema = HebergementFolder_schema

    ##code-section class-header #fill in your manual code here
    implements(IHebergementFolder)
    ##/code-section class-header

    # Methods

    # Manually created methods

    security.declarePrivate('_createUniqueId')
    def _createUniqueId(self, dupId, idList):
        cpt = 1
        while 1:
            new_id = "%s-%s" % (dupId, cpt)
            cpt += 1
            if new_id not in idList:
                id = new_id
                break
        return id

    security.declareProtected("Modify portal content", 'updateHebergement')
    def updateHebergement(self):
        portal = getToolByName(self, 'portal_url').getPortalObject()
        ptool = portal.plone_utils
        wrapper = getSAWrapper('gites_wallons')
        Hebergement = wrapper.getMapper('hebergement')
        session = wrapper.session
        hebergements = session.query(Hebergement).all()
        self.known_gites_id = PersistentDict()
        for hebergement in hebergements:
            nom = hebergement.heb_nom
            id = hebergement.heb_id
            if not id:
                id = ptool.normalizeString(nom)
                if id in self.known_gites_id.keys():
                    id = self._createUniqueId(id, self.known_gites_id.keys())
                hebergement.heb_id = id
                session.update(hebergement)
            self.known_gites_id[id] = hebergement.heb_pk

    security.declareProtected("Modify portal content", 'updateType')
    def updateType(self):
        portal = getToolByName(self, 'portal_url').getPortalObject()
        ptool = portal.plone_utils
        wrapper = getSAWrapper('gites_wallons')
        TypesHeb = wrapper.getMapper('type_heb')
        session = wrapper.session
        typesHebs = session.query(TypesHeb).all()
        self.known_types_id = PersistentDict()
        for typeHeb in typesHebs:
            nom = typeHeb.type_heb_nom
            pk = typeHeb.type_heb_pk
            id = typeHeb.type_heb_id
            if not id:
                id = ptool.normalizeString(nom)
                if id in self.known_types_id.keys():
                    id = self._createUniqueId(id, self.known_types_id.keys())
                typeHeb.type_heb_id = id
                session.update(typeHeb)
            self.known_types_id[id] = pk

            nom = typeHeb.type_heb_nom_nl
            id = typeHeb.type_heb_id_nl
            if not id:
                id = ptool.normalizeString(nom)
                if id in self.known_types_id.keys():
                    id = self._createUniqueId(id, self.known_types_id.keys())
                typeHeb.type_heb_id_nl = id
                session.update(typeHeb)
            self.known_types_id[id] = pk

            nom = typeHeb.type_heb_nom_uk
            id = typeHeb.type_heb_id_uk
            if not id:
                id = ptool.normalizeString(nom)
                if id in self.known_types_id.keys():
                    id = self._createUniqueId(id, self.known_types_id.keys())
                typeHeb.type_heb_id_uk = id
                session.update(typeHeb)
            self.known_types_id[id] = pk

            id = typeHeb.type_heb_id_de
            nom = typeHeb.type_heb_nom_de
            if not id:
                id = ptool.normalizeString(nom)
                if id in self.known_types_id.keys():
                    id = self._createUniqueId(id, self.known_types_id.keys())
                typeHeb.type_heb_id_de = id
                session.update(typeHeb)
            self.known_types_id[id] = pk

            nom = typeHeb.type_heb_nom_it
            id = typeHeb.type_heb_id_it
            if not id:
                id = ptool.normalizeString(nom)
                if id in self.known_types_id.keys():
                    id = self._createUniqueId(id, self.known_types_id.keys())
                typeHeb.type_heb_id_it = id
                session.update(typeHeb)
            self.known_types_id[id] = pk

    security.declareProtected("Modify portal content", 'updateCommune')
    def updateCommune(self):
        portal = getToolByName(self, 'portal_url').getPortalObject()
        ptool = portal.plone_utils
        wrapper = getSAWrapper('gites_wallons')
        Commune = wrapper.getMapper('commune')
        session = wrapper.session
        communes = session.query(Commune).all()
        self.known_communes_id = PersistentDict()
        for commune in communes:
            nom = commune.com_nom
            id = commune.com_id
            if not id:
                id = ptool.normalizeString(nom)
                commune.com_id = id
                session.update(commune)
            self.known_communes_id[id] = commune.com_pk

    security.declareProtected("Modify portal content", 'updateHebergement')
    def update(self, REQUEST=None):
        """
        """
        self.updateHebergement()
        self.updateCommune()
        self.updateType()

    def view(self, REQUEST):
        """
        default give back a search form
        """
        url = "%s/search.html" % self.absolute_url()
        return REQUEST.RESPONSE.redirect(url)


registerType(HebergementFolder, PROJECTNAME)
