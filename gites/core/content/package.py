# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from plone.app.folder import folder
from plone.app.blob.field import ImageField
from Products.CMFCore.interfaces import IContentish
from Products.Archetypes.Field import DateTimeField, LinesField
from Products.Archetypes.Widget import CalendarWidget
from plone.widgets.archetypes import ChosenWidget
from Products.Archetypes.interfaces import (IBaseFolder,
                                            IBaseObject,
                                            IReferenceable)
from Products import DataGridField
from Products.ATContentTypes.content.folder import ATFolder
from Products.LinguaPlone.public import (Schema, TextField, RichWidget,
                                         ImageWidget,
                                         TextAreaWidget, registerType)

from monet.mapsviewlet.interfaces import IMonetMapsEnabledContent

from gites.core.config import PROJECTNAME
from gites.core.content.interfaces import IPackage
from gites.core.browser.vocabulary import CriteriaVocabularyFactory


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
            description="Description détaillée du produit",
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

    DateTimeField(
        name='startDate',
        languageIndependent=True,
        required=0,
        widget=CalendarWidget(
            label="Date de début de l'évenement",
            description="Date de début servant de filtre pour les disponibilités des hébergements",
        ),
    ),

    DateTimeField(
        name='endDate',
        languageIndependent=True,
        required=0,
        widget=CalendarWidget(
            label="Date de fin de l'évenement",
            description="Date de fin servant de filtre pour les disponibilités des hébergements",
        ),
    ),

    DataGridField.DataGridField(
        name='criteria',
        schemata=u'Criteres',
        columns=('criterion', 'value'),
        widget=DataGridField.DataGridWidget
        (
            label='Critères',
            label_msgid='GitesContent_label_criteria',
            i18n_domain='gites',
            columns={'criterion': DataGridField.SelectColumn(u'Critères de sélection des hébergements pour ce produit',
                                                             vocabulary=CriteriaVocabularyFactory),
                     'value': DataGridField.CheckboxColumn(u'')}
        ),
    ),
    LinesField(
        name='userCriteria',
        multiValued=1,
        vocabulary=CriteriaVocabularyFactory,
        widget=ChosenWidget(
            description="""Critères à choisir par l'utilisateur""",
            label='User Criteria',
            label_msgid='gites_core_package_usercriteria_label',
            description_msgid='gites_core_packages_usercriteria_description',
            i18n_domain='gites',
        ))

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

##code-section after-schema #fill in your manual code here
Package_schema = folder.ATFolderSchema + schema.copy()
Package_schema['location'].widget.visible = False
Package_schema.changeSchemataForField('startDate', 'dates')
Package_schema.changeSchemataForField('endDate', 'dates')


class Package(ATFolder):
    """
    """
    security = ClassSecurityInfo()
    implements(IPackage, IBaseFolder, IBaseObject, IReferenceable,
               IContentish, IMonetMapsEnabledContent)

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
