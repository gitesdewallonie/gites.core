# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from gites.core.config import PROJECTNAME
from gites.core.widgets import DBReferenceWidget
from zope.interface import implements
from gites.core.content.interfaces import IPackage
from plone.app.folder import folder
from Products.CMFCore.interfaces import IContentish
from Products.Archetypes.interfaces import (IBaseFolder,
                                            IBaseObject,
                                            IReferenceable)
from plone.app.blob.field import ImageField
from Products.LinguaPlone.public import (Schema, TextField, RichWidget,
                                         ImageWidget, LinesField,
                                         TextAreaWidget, registerType)


schema = Schema((

    TextField(
        name='description',
        widget=TextAreaWidget(
            description="Description succinte du produit",
            label='Description',
            label_msgid='GitesContent_label_description',
            description_msgid='GitesContent_help_description',
            i18n_domain='gites',
        )
    ),

    TextField(
        name='text',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword'),
        widget=RichWidget(
            description="Description detaillee du produit",
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

    LinesField(
        name='hebergements',
        widget=DBReferenceWidget
        (
            label="Hebergements Concernes",
            description="Liste des hebergements concernes par ce package",
            label_msgid='GitesContent_label_hebergements',
            description_msgid='GitesContent_help_hebergements',
            i18n_domain='gites',
        ),
        multiValued=1
    ),

),
)

##code-section after-local-schema #fill in your manual code here
schema['hebergements'].widget.table = 'hebergement'
schema['hebergements'].widget.unique_column = 'heb_pk'
schema['hebergements'].widget.default_columns = 'heb_nom'
schema['hebergements'].widget.viewable_columns = {'heb_nom': 'Nom'}
schema['hebergements'].languageIndependent = True
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

    meta_type = 'Package'
    portal_type = 'Package'
    allowed_content_types = ['Vignette', 'Image']
    filter_content_types = 1
    global_allow = 1
    #content_icon = 'Package.gif'
    immediate_view = 'package_view'
    default_view = 'package_view'
    suppl_views = ()
    typeDescription = "Package"
    typeDescMsgId = 'description_edit_package'

    actions = (
        {'action': "string:${object_url}/package_view",
         'category': "object",
         'id': 'view',
         'name': 'View',
         'permissions': ("View", ),
         'condition': 'python:1'},
    )

    _at_rename_after_creation = True

    schema = Package_schema


InitializeClass(Package)
registerType(Package, PROJECTNAME)
