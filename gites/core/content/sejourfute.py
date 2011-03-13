# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from sqlalchemy import select, and_
from AccessControl import ClassSecurityInfo
from gites.core.config import PROJECTNAME
from gites.core.widgets import DBReferenceWidget
from zope.interface import implements
from z3c.sqlalchemy import getSAWrapper
from gites.core.content.interfaces import ISejourFute
from Products.ATContentTypes.content.folder import ATFolder
from Products.LinguaPlone.public import (Schema, TextField, TextAreaWidget,
                                         RichWidget, LinesField, DateTimeField,
                                         CalendarWidget, BaseFolderSchema,
                                         registerType)

schema = Schema((

    TextField(
        name='description',
        widget=TextAreaWidget(
            description="Description succinte du sejour fute",
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
            description="""Texte
            Une description detaillee du sejour fute""",
            searchable=1,
            label='Text',
            label_msgid='GitesContent_label_text',
            description_msgid='GitesContent_help_text',
            i18n_domain='gites',
        ),
        default_output_type='text/html',
        required=1
    ),

    LinesField(
        name='maisonsTourisme',
        widget=DBReferenceWidget
        (
            description="""Maisons du tourisme
            Les maisons du tourismes concernees par ce type de sejour fute""",
            label='Maisonstourisme',
            label_msgid='GitesContent_label_maisonsTourisme',
            description_msgid='GitesContent_help_maisonsTourisme',
            i18n_domain='gites',
        ),
        multiValued=1
    ),

    LinesField(
        name='hebergementsConcernes',
        widget=DBReferenceWidget
        (
            description="Liste des hebergements concernes",
            label='Hebergementsconcernes',
            label_msgid='GitesContent_label_hebergementsConcernes',
            description_msgid='GitesContent_help_hebergementsConcernes',
            i18n_domain='gites',
        ),
        multiValued=1
    ),

    DateTimeField(
        name='startDate',
        mutator="setStart",
        widget=CalendarWidget(
            description="""Date d'activation
            Date a laquelle le sejour apparaitra""",
            label='Startdate',
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
            description="""Date de retrait
            Date a laquelle le sejour n apparaitra plus""",
            show_hm=False,
            label='Enddate',
            label_msgid='GitesContent_label_endDate',
            description_msgid='GitesContent_help_endDate',
            i18n_domain='gites',
        ),
        required=1,
        languageIndependent=1
    ),

),
)

##code-section after-local-schema #fill in your manual code here
schema['maisonsTourisme'].widget.table = 'maison_tourisme'
schema['maisonsTourisme'].widget.unique_column = 'mais_pk'
schema['maisonsTourisme'].widget.default_columns = 'mais_nom'
schema['maisonsTourisme'].widget.viewable_columns = {'mais_nom': 'Nom'}
schema['maisonsTourisme'].languageIndependent = True

schema['hebergementsConcernes'].widget.table = 'hebergement'
schema['hebergementsConcernes'].widget.unique_column = 'heb_pk'
schema['hebergementsConcernes'].widget.default_columns = 'heb_nom'
schema['hebergementsConcernes'].widget.viewable_columns = {'heb_nom': 'Nom'}
schema['hebergementsConcernes'].languageIndependent = True

##/code-section after-local-schema

SejourFute_schema = BaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
SejourFute_schema = ATFolder.schema.copy() + \
    schema.copy()
##/code-section after-schema


class SejourFute(ATFolder):
    """
    """
    security = ClassSecurityInfo()
    implements(ISejourFute)
    __implements__ = (getattr(ATFolder, '__implements__', ()))

    # This name appears in the 'add' box
    archetype_name = 'Sejour Fute'

    meta_type = 'SejourFute'
    portal_type = 'SejourFute'
    allowed_content_types = ['ATImage', 'Vignette', 'Vignette', 'Image']
    filter_content_types = 1
    global_allow = 1
    #content_icon = 'SejourFute.gif'
    immediate_view = 'sejour_fute_view'
    default_view = 'sejour_fute_view'
    suppl_views = ()
    typeDescription = "Sejour Fute"
    typeDescMsgId = 'description_edit_sejourfute'


    actions = (
       {'action': "string:${object_url}/sejour_fute_view",
        'category': "object",
        'id': 'view',
        'name': 'View',
        'permissions': ("View", ),
        'condition': 'python:1'}, )

    _at_rename_after_creation = True

    schema = SejourFute_schema


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

    def end(self):
        return self.getEndDate()

    def start(self):
        return self.getStartDate()

    def getVignettes(self):
        return self.objectValues('Vignette')

    def getImages(self):
        return self.objectValues('ATImage')

    related_heb_pks = None

    def getHebPks(self):
        if self.related_heb_pks is None:
            hebs = [int(heb_pk) for heb_pk in self.getHebergementsConcernes()]
            maisonTourismes = [int(i) for i in self.getMaisonsTourisme()]
            wrapper = getSAWrapper('gites_wallons')
            MaisonTourisme = wrapper.getMapper('maison_tourisme')
            Commune = wrapper.getMapper('commune')
            Hebergement = wrapper.getMapper('hebergement')
            session = wrapper.session
            query = select([Hebergement.heb_pk])
            query.append_whereclause(and_(Commune.com_pk == Hebergement.heb_com_fk,
                                          Commune.com_mais_fk == MaisonTourisme.mais_pk,
                                          MaisonTourisme.mais_pk.in_(maisonTourismes)))
            hebIds = session.execute(query).fetchall()
            hebs.extend([heb.heb_pk for heb in hebIds])
            self.related_heb_pks = hebs
        return self.related_heb_pks

    security.declareProtected("View", 'post_validate')

    def post_validate(self, REQUEST=None, errors=None):
        """Validates start and end date

        End date must be after start date
        """
        self.related_heb_pks = None
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


registerType(SejourFute, PROJECTNAME)
