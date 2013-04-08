#NOCHECK
import logging
logger = logging.getLogger('gites.core')
logger.debug('Installing Product')

from Products.Archetypes import listTypes
from Products.Archetypes.atapi import process_types
from Products.CMFCore import utils as cmfutils
from config import PROJECTNAME, DEFAULT_ADD_CONTENT_PERMISSION
from gites.core.permissions import initialize as initialize_permissions


def initialize(context):
    ##code-section custom-init-top #fill in your manual code here
    ##/code-section custom-init-top

    # imports packages and types for registration
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = atype.archetype_name
        cmfutils.ContentInit(
            kind,
            content_types=(atype,),
            permission=DEFAULT_ADD_CONTENT_PERMISSION,
            extra_constructors=(constructor,),
            ).initialize(context)
    # Initialize the permissions
    initialize_permissions()
