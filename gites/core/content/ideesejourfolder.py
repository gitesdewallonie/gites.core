# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from AccessControl import ClassSecurityInfo
from gites.core.config import PROJECTNAME
from zope.interface import implements
from gites.core.content.interfaces import IIdeeSejourFolder
from Products.LinguaPlone.public import (Schema, TextField, RichWidget,
                                         ImageField,
                                         ImageWidget, AttributeStorage,
                                         OrderedBaseFolderSchema,
                                         OrderedBaseFolder,
                                         registerType)

schema = Schema((

    TextField(
        name='description',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword', ),
        widget=RichWidget(
            label="Description",
            description="Describe the sejour folder here",
            label_msgid='GitesContent_label_description',
            description_msgid='GitesContent_help_description',
            i18n_domain='GitesContent',
        ),
        default_output_type='text/html'
    ),
    ImageField(
        name='logo',
        widget=ImageWidget(
            label='Logo',
            label_msgid='GitesContent_label_logo',
            i18n_domain='GitesContent',
        ),
        storage=AttributeStorage()
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

IdeeSejourFolder_schema = OrderedBaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class IdeeSejourFolder(OrderedBaseFolder):
    """
    """
    security = ClassSecurityInfo()
    implements(IIdeeSejourFolder)
    __implements__ = (getattr(OrderedBaseFolder, '__implements__', ()))

    # This name appears in the 'add' box
    archetype_name = 'IdeeSejourFolder'

    meta_type = 'IdeeSejourFolder'
    portal_type = 'IdeeSejourFolder'
    allowed_content_types = ['ATImage', 'IdeeSejourFolder', 'IdeeSejour', 'Vignette']
    filter_content_types = 1
    global_allow = 0
    #content_icon = 'IdeeSejourFolder.gif'
    immediate_view = 'idee_sejour_folder'
    default_view = 'idee_sejour_folder'
    suppl_views = ()
    typeDescription = "IdeeSejourFolder"
    typeDescMsgId = 'description_edit_ideesejourfolder'


    actions = (
       {'action': "string:${object_url}/idee_sejour_folder",
        'category': "object",
        'id': 'view',
        'name': 'View',
        'permissions': ("View", ),
        'condition': 'python:1'},
    )

    _at_rename_after_creation = True

    schema = IdeeSejourFolder_schema

    ##code-section class-header #fill in your manual code here
    global_allow = 1
    aliases = {
        '(Default)': 'idee_sejour_folder',
        'view': 'idee_sejour_folder',
        'index.html': '(dynamic view)',
        'edit': 'atct_edit',
        'properties': 'base_metadata',
        'sharing': 'folder_localrole_form',
        'gethtml': '',
        'mkdir': '',
        }


registerType(IdeeSejourFolder, PROJECTNAME)
