# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from gites.core.config import PROJECTNAME
from zope.interface import implements
from gites.core.content.interfaces import IPackage
from plone.app.folder import folder
from Products.CMFCore.interfaces import IContentish
from Products.Archetypes.interfaces import (IBaseFolder,
                                            IBaseObject,
                                            IReferenceable)
from plone.app.blob.field import ImageField
from Products import DataGridField
from Products.LinguaPlone.public import (Schema, TextField, RichWidget,
                                         ImageWidget, registerType)


schema = Schema((

    TextField(
        name='text',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword'),
        widget=RichWidget(
            description="Contenu de la description du type de sejour",
            label='Text',
            label_msgid='GitesContent_label_text',
            description_msgid='GitesContent_help_text',
            i18n_domain='gites',
        ),
        default_output_type='text/html'
    ),

    ImageField(
        name='logo',
        widget=ImageWidget(
            label='Logo',
            label_msgid='GitesContent_label_logo',
            i18n_domain='gites',
        ),
    ),

    DataGridField.DataGridField(
        name='criteria',
        columns=('criterion', 'value'),
        widget=DataGridField.DataGridWidget
        (
            columns={'criterion': DataGridField.SelectColumn(u'Criteria',
                                                             vocabulary=''),
                     'value': DataGridField.CheckboxColumn(u'')}
        ),
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

##code-section after-schema #fill in your manual code here
Package_schema = folder.ATFolderSchema + schema.copy()

##/code-section after-schema


class Package(folder.ATFolder):
    """
    """
    security = ClassSecurityInfo()
    implements(IPackage, IBaseFolder, IBaseObject, IReferenceable, IContentish)

    # This name appears in the 'add' box
    archetype_name = 'Package'
    session_name = 'pg'
    item_class = None

    meta_type = 'Package'
    portal_type = 'Package'
    allowed_content_types = ['Vignette']
    filter_content_types = 1
    global_allow = 0
    #content_icon = 'Package.gif'
    immediate_view = 'package'
    default_view = 'package'
    suppl_views = ('package_listing', )
    typeDescription = "Package"
    typeDescMsgId = 'description_edit_package'

    actions = (
        {'action': "string:${object_url}/package",
         'category': "object",
         'id': 'view',
         'name': 'View',
         'permissions': ("View", ),
         'condition': 'python:1'},
    )

    _at_rename_after_creation = True
    schema = Package_schema
    global_allow = 1


InitializeClass(Package)
registerType(Package, PROJECTNAME)
