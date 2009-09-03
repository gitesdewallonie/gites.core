# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from AccessControl import ClassSecurityInfo
from gites.core.config import PROJECTNAME
from gites.core.widgets import DBReferenceWidget
from zope.interface import implements
from gites.core.content.interfaces import IIdeeSejour
from Products.ATContentTypes.content.folder import ATFolder
from Products.LinguaPlone.public import (Schema, TextField, RichWidget,
                                         ImageField, ImageWidget,
                                         AttributeStorage, LinesField,
                                         BaseFolderSchema, registerType)

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
        storage=AttributeStorage()
    ),

    LinesField(
        name='hebergements',
        widget=DBReferenceWidget
        (
            label="Hebergements Concernes",
            description="Liste des hebergements concernes par cet idee sejour",
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
schema['hebergements'].languageIndependent=True
##/code-section after-local-schema

IdeeSejour_schema = BaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
IdeeSejour_schema = ATFolder.schema.copy() + \
    schema.copy()

##/code-section after-schema

class IdeeSejour(ATFolder):
    """
    """
    security = ClassSecurityInfo()
    implements(IIdeeSejour)
    __implements__ = (getattr(ATFolder, '__implements__', ()))

    # This name appears in the 'add' box
    archetype_name = 'IdeeSejour'

    meta_type = 'IdeeSejour'
    portal_type = 'IdeeSejour'
    allowed_content_types = ['Vignette', 'ATImage', 'Vignette', 'Image']
    filter_content_types = 1
    global_allow = 0
    #content_icon = 'IdeeSejour.gif'
    immediate_view = 'idee_sejour'
    default_view = 'idee_sejour'
    suppl_views = ('idee_sejour_listing', )
    typeDescription = "IdeeSejour"
    typeDescMsgId = 'description_edit_ideesejour'

    actions = (
       {'action': "string:${object_url}/idee_sejour",
        'category': "object",
        'id': 'view',
        'name': 'View',
        'permissions': ("View", ),
        'condition': 'python:1'},
    )

    _at_rename_after_creation = True

    schema = IdeeSejour_schema

    global_allow = 1

registerType(IdeeSejour, PROJECTNAME)
