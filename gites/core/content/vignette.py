# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.image import ATImage
from gites.core.config import PROJECTNAME
from Products.LinguaPlone.public import (Schema, registerType)

schema = Schema((
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Vignette_schema = getattr(ATImage, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
Vignette_schema['image'].sizes['thumb'] = (130, 107)
Vignette_schema['image'].languageIndependent = True


##/code-section after-schema

class Vignette(ATImage):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(ATImage, '__implements__', ()))

    # This name appears in the 'add' box
    archetype_name = 'Vignette'

    meta_type = 'Vignette'
    portal_type = 'Vignette'
    allowed_content_types = [] + list(getattr(ATImage, 'allowed_content_types', []))
    filter_content_types = 0
    global_allow = 0
    #content_icon = 'Vignette.gif'
    immediate_view = 'image_view'
    default_view = 'image_view'
    suppl_views = ()
    typeDescription = "Vignette"
    typeDescMsgId = 'description_edit_vignette'

    _at_rename_after_creation = True

    schema = Vignette_schema
    global_allow = 1

registerType(Vignette, PROJECTNAME)
