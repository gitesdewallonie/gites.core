# -*- coding: utf-8 -*-
#
# File: BoutiqueItem.py
#
# Copyright (c) 2008 by Affinitic
# Generator: ArchGenXML Version 1.6.0-beta-svn
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """Jean Francois Roche <jfroche@pyxel.be>"""
__docformat__ = 'plaintext'

from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import (Schema, registerType,
                                       TextField, RichWidget, ImageField,
                                       ImageWidget, AttributeStorage,
                                       BaseFolderSchema)
from gites.core.config import PROJECTNAME
from gites.core.content.interfaces import IBoutiqueItem
from Products.ATContentTypes.content.folder import ATFolder


schema = Schema((

    TextField(
        name='text',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword'),
        widget=RichWidget(
            label='Text',
            label_msgid='GitesContent_label_text',
            i18n_domain='gites',
        ),
        default_output_type='text/html',
        required=1
    ),

    ImageField(
        name='photo',
        widget=ImageWidget(
            label='Photo',
            label_msgid='GitesContent_label_photo',
            i18n_domain='gites',
        ),
        required=1,
        storage=AttributeStorage()
    ),

),
)

##code-section after-local-schema #fill in your manual code here
schema['photo'].sizes = {'large': (768, 768),
                         'preview': (400, 400),
                         'mini': (200, 200),
                         'thumb': (128, 128),
                         'tile': (64, 64)}
##/code-section after-local-schema

BoutiqueItem_schema = BaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
BoutiqueItem_schema = ATFolder.schema.copy() + \
    schema.copy()

##/code-section after-schema


class BoutiqueItem(ATFolder):
    """
    """
    implements(IBoutiqueItem)
    security = ClassSecurityInfo()
    __implements__ = (getattr(ATFolder, '__implements__', ()))

    # This name appears in the 'add' box
    archetype_name = 'BoutiqueItem'

    meta_type = 'BoutiqueItem'
    portal_type = 'BoutiqueItem'
    allowed_content_types = ['ATImage', 'Vignette', 'Image']
    filter_content_types = 1
    global_allow = 1
    #content_icon = 'BoutiqueItem.gif'
    immediate_view = 'boutique_item_view'
    default_view = 'boutique_item_view'
    suppl_views = ()
    typeDescription = "BoutiqueItem"
    typeDescMsgId = 'description_edit_boutiqueitem'

    actions = (

        {'action': "string:${object_url}/boutique_item_view",
         'category': "object",
         'id': 'view',
         'name': 'View',
         'permissions': ("View", ),
         'condition': 'python:1'},

    )

    _at_rename_after_creation = True

    schema = BoutiqueItem_schema

    def getMiniPhoto(self):
        return self.getField('photo').tag(self, scale='thumb',
                                          title=self.Description())


registerType(BoutiqueItem, PROJECTNAME)
