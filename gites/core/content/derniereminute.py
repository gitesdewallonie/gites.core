# -*- coding: utf-8 -*-
#
# File: DerniereMinute.py
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

from AccessControl import ClassSecurityInfo
from zope.interface import implements
from gites.core.config import PROJECTNAME
from gites.core.widgets import DBReferenceWidget
from gites.core.content.interfaces import IDerniereMinute
from Products.ATContentTypes.content.folder import ATFolder
from z3c.sqlalchemy import getSAWrapper
from Products.LinguaPlone.public import (Schema, TextField, RichWidget,
                                         StringField, SelectionWidget,
                                         LinesField, DateTimeField,
                                         CalendarWidget, BaseSchema,
                                         registerType)

schema = Schema((

    TextField(
        name='text',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword'),
        widget=RichWidget(
            description="""Texte
            Descriptif de la promotion - dernieres minutes""",
            searchable=1,
            label='Text',
            label_msgid='GitesContent_label_text',
            description_msgid='GitesContent_help_text',
            i18n_domain='gites',
        ),
        default_output_type='text/html',
        required=0
    ),

    StringField(
        name='category',
        widget=SelectionWidget(
            description="""Type
            Type de derniere minute""",
            label='Category',
            label_msgid='GitesContent_label_category',
            description_msgid='GitesContent_help_category',
            i18n_domain='gites',
        ),
        required=1,
        multiValued=0,
        vocabulary='getAvailableCategories'
    ),

    LinesField(
        name='hebergementsConcernes',
        widget=DBReferenceWidget
        (
            description="""Hebergement concerne
            Hebergement concerne par la promotion ou la derniere minute""",
            label='Hebergementsconcernes',
            label_msgid='GitesContent_label_hebergementsConcernes',
            description_msgid='GitesContent_help_hebergementsConcernes',
            i18n_domain='gites',
        ),
        multiValued=0
    ),

    DateTimeField(
        name='startDate',
        mutator="setStart",
        widget=CalendarWidget(
            label="Date de debut de publication",
            description="Date a laquelle la derniere minute - promotion est publie",
            label_msgid='GitesContent_label_startDate',
            description_msgid='GitesContent_help_startDate',
            i18n_domain='gites',
        ),
        required=1,
        show_hm=False,
        languageIndependent=1
    ),

    DateTimeField(
        name='endDate',
        mutator="setEnd",
        widget=CalendarWidget(
            description="""Date de fin de publication
            Date de fin de la publication de la derniere minute""",
            label='Enddate',
            label_msgid='GitesContent_label_endDate',
            description_msgid='GitesContent_help_endDate',
            i18n_domain='gites',
        ),
        required=1,
        show_hm=False,
        languageIndependent=1
    ),

    DateTimeField(
        name='eventStartDate',
        widget=CalendarWidget(
            show_hm=False,
            description="""Debut de l evenement
            Date a laquelle l evenement commence""",
            label='Eventstartdate',
            label_msgid='GitesContent_label_eventStartDate',
            description_msgid='GitesContent_help_eventStartDate',
            i18n_domain='gites',
        ),
        languageIndependent=1,
        required=1
    ),

    DateTimeField(
        name='eventEndDate',
        widget=CalendarWidget(
            show_hm=False,
            description="Date a laquelle l evenement se fini",
            label="Fin de l evenement",
            label_msgid='GitesContent_label_eventEndDate',
            description_msgid='GitesContent_help_eventEndDate',
            i18n_domain='gites',
        ),
        languageIndependent=1,
        required=1
    ),

),
)

##code-section after-local-schema #fill in your manual code here
schema['hebergementsConcernes'].widget.table = 'hebergement'
schema['hebergementsConcernes'].widget.unique_column = 'heb_pk'
schema['hebergementsConcernes'].widget.default_columns = 'heb_nom'
schema['hebergementsConcernes'].widget.viewable_columns = {'heb_nom': 'Nom'}
schema['hebergementsConcernes'].languageIndependent=True

##/code-section after-local-schema

DerniereMinute_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
DerniereMinute_schema = ATFolder.schema.copy() + \
    schema.copy()
DerniereMinute_schema['description'].widget.visible={'view': 'invisible',
                                                     'edit': 'invisible'}

##/code-section after-schema

class DerniereMinute(ATFolder):
    """
    """
    security = ClassSecurityInfo()
    implements(IDerniereMinute)
    __implements__ = (getattr(ATFolder, '__implements__', ()))

    # This name appears in the 'add' box
    archetype_name = 'DerniereMinute'

    meta_type = 'DerniereMinute'
    portal_type = 'DerniereMinute'
    allowed_content_types = ['ATImage']
    filter_content_types = 0
    global_allow = 1
    #content_icon = 'DerniereMinute.gif'
    immediate_view = 'derniere_minute_view'
    default_view = 'derniere_minute_view'
    suppl_views = ()
    typeDescription = "DerniereMinute"
    typeDescMsgId = 'description_edit_derniereminute'


    actions = (
       {'action': "string:${object_url}/derniere_minute_view",
        'category': "object",
        'id': 'view',
        'name': 'View',
        'permissions': ("View", ),
        'condition': 'python:1'},
    )

    _at_rename_after_creation = True

    schema = DerniereMinute_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('getAvailableCategories')

    def getAvailableCategories(self):
        """
        """
        from Products.Archetypes.utils import DisplayList
        dl = DisplayList()
        dl.add('derniere-minute', u'Dernières minutes')
        dl.add('promotion', u'Promotion')
        return dl

    security.declareProtected("Modify portal content", 'setStart')

    def setStart(self, value, **kwargs):
        """
        """
        f = self.getField('startDate')
        f.set(self, value, **kwargs)
        f = self.getField('effectiveDate')
        f.set(self, value, **kwargs)

    security.declareProtected("Modify portal content", 'setEnd')

    def setEnd(self, value, **kwargs):
        """
        """
        f = self.getField('endDate')
        f.set(self, value, **kwargs)
        f = self.getField('expirationDate')
        f.set(self, value, **kwargs)

    # Manually created methods

    security.declareProtected("View", 'post_validate')

    def post_validate(self, REQUEST=None, errors=None):
        """Validates start and end date

        End date must be after start date
        """
        rstartDate = REQUEST.get('startDate', None)
        rendDate = REQUEST.get('endDate', None)
        from DateTime import DateTime

        if rendDate:
            end = DateTime(rendDate)
        else:
            end = self.getEndDate()
        if rstartDate:
            start = DateTime(rstartDate)
        else:
            start = self.getStartDate()

        if start > end:
            errors['endDate'] = "End date must be after start date"

    def end(self):
        return self.getEndDate()

    def start(self):
        return self.getStartDate()

    def getHebergement(self):
        heb = self.getHebergementsConcernes()
        if heb and heb[0] != '()':
            wrapper = getSAWrapper('gites_wallons')
            Hebergements = wrapper.getMapper('hebergement')
            session = wrapper.session
            hebergement = session.query(Hebergements).filter(Hebergements.heb_pk==self.getHebergementsConcernes()[0]).one()
            return hebergement.__of__(self.hebergement)
        else:
            return None


registerType(DerniereMinute, PROJECTNAME)
