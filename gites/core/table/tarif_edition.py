# encoding: utf-8
"""
gites.pivot.core

Created by schminitz
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

import zope.component
import zope.interface
import zope.publisher
from zope.component import getUtility
from zope.i18n import translate
from zope.schema.interfaces import IVocabularyFactory
from five import grok
from plone import api

from z3c.table import column, interfaces as table_interfaces, table, value

from gites.core import interfaces
from gites.db.content import Tarifs, TarifsType, Hebergement
from gites.locales import GitesMessageFactory as _


class TarifEditionTable(table.Table):
    zope.interface.implements(interfaces.ITarifEditionTable)

    cssClasses = {'table': 'z3c-listing percent100 listing nosort'}
    cssClassEven = u'odd'
    cssClassOdd = u'even'
    sortOn = None
    startBatchingAt = 9999

    tarif_min_subtypes = [
        'WEEK',
        'WEEKEND',
        '3_NIGHTS',
        '4_NIGHTS',
        '1_PERSON',
        '2_PERSONS',
        'PERSON_SUP',
        'WITHOUT_BREAKFAST',
        'END_OF_YEAR',
        'GUARANTEE',
    ]

    tarif_max_subtypes = [
        'WEEK',
        'WEEKEND',
        '3_NIGHTS',
        '4_NIGHTS',
        'END_OF_YEAR',
    ]

    tarif_cmt_subtypes = [
        'ACCORDING_TO_CONSUMPTION',
        'INCLUDED',
        'INCLUSIVE',
        'TABLE_HOTES',
        'OTHER',
        'SOJOURN_TAX',
    ]

    def __init__(self, context, request):
        super(TarifEditionTable, self).__init__(context, request)
        self.heb_pk = self.request.get('heb_pk', None)

    @property
    def values(self):
        """ Returns the values for an hosting """
        adapter = zope.component.getMultiAdapter(
            (self.context, self.request, self), table_interfaces.IValues)
        return adapter.values


class TarifEditionValues(value.ValuesMixin,
                         grok.MultiAdapter):
    grok.provides(table_interfaces.IValues)
    grok.adapts(zope.interface.Interface,
                zope.publisher.interfaces.browser.IBrowserRequest,
                interfaces.ITarifEditionTable)

    @property
    def values(self):
        heb = self._get_heb()

        if heb.type.type_heb_type == 'gite':
            tarifs_types = TarifsType.get(gite=True)
        else:
            tarifs_types = TarifsType.get(chambre=True)

        self.tarifs = Tarifs.get_hebergement_tarifs(heb.heb_pk)
        tarifs_table = []
        for tarifs_type in tarifs_types:
            tarifs_table.append(self._get_tarif_line(tarifs_type))
        return tarifs_table

    def _get_heb(self):
        roles = api.user.get_current().getRoles()
        heb = None

        # Proprio of heb in the request?
        if 'Proprietaire' in roles:
            proprio_hebs = getUtility(IVocabularyFactory, name='proprio.hebergements')(self.context)
            for proprio_heb in proprio_hebs:
                if proprio_heb.token == self.table.heb_pk:
                    heb = Hebergement.first(heb_pk=self.table.heb_pk)
                    break

        # Admin
        elif 'Manager' in roles:
            heb = Hebergement.first(heb_pk=self.table.heb_pk)

        return heb

    def _get_tarif_line(self, tarifs_type):
        for tarif in self.tarifs:
            if (tarif.type == tarifs_type.type and
               tarif.subtype == tarifs_type.subtype):
                return tarif
        return tarifs_type


class TarifEditionColumn(column.GetAttrColumn):
    """ Base class for the comparison columns """
    grok.provides(table_interfaces.IColumn)
    grok.adapts(zope.interface.Interface,
                zope.interface.Interface,
                interfaces.ITarifEditionTable)

    def translate(self, msgid):
        language = self.request.get('LANGUAGE', 'fr')
        return translate(_(msgid), target_language=language)


class TarifEditionColumnType(TarifEditionColumn, grok.MultiAdapter):
    grok.name('type')
    header = u'Type'
    attrName = u'type'
    weight = 10

    def renderCell(self, item):
        value = getattr(item, 'type', '') or ''
        return self.translate(value)


class TarifEditionColumnSubtype(TarifEditionColumn, grok.MultiAdapter):
    grok.name('subtype')
    header = u'Sous-Type'
    attrName = u'subtype'
    weight = 20

    def renderCell(self, item):
        value = getattr(item, 'subtype', '') or ''
        return self.translate(value)


class TarifEditionColumnDate(TarifEditionColumn, grok.MultiAdapter):
    grok.name('date')
    header = u'Date'
    weight = 30

    def renderCell(self, item):
        tarif_date = getattr(item, 'date', None)
        return tarif_date and tarif_date.strftime('%d-%m-%Y') or ''


class TarifEditionColumnUser(TarifEditionColumn, grok.MultiAdapter):
    grok.name('user')
    header = u'Utilisateur'
    attrName = u'user'
    weight = 40


class TarifEditionColumnValues(TarifEditionColumn, grok.MultiAdapter):
    grok.adapts(zope.interface.Interface,
                zope.interface.Interface,
                interfaces.ITarifEditionToConfirm)
    grok.name('values')
    header = u'Valeurs actuelles'
    weight = 50

    def renderCell(self, item):
        elements = [self.render_field(item, 'min', after=u' €'),
                    self.render_field(item, 'max', after=u' €', before=' / '),
                    self.render_field(item, 'cmt')]
        return u''.join(elements)

    def render_field(self, item, attr, before=u'', after=u''):
        subtypes = getattr(self.table, 'tarif_{0}_subtypes'.format(attr))
        if item.subtype not in subtypes:
            return u''

        value = getattr(item, attr, '') or ''
        input_text = (u'{0}{1}{2}')
        return input_text.format(before, value, after)


class TarifEditionColumnInputsMixin(TarifEditionColumn, grok.MultiAdapter):
    grok.name('inputs')
    header = u''
    weight = 60

    def get_item(self, item):
        raise NotImplementedError

    def renderCell(self, item):
        item = self.get_item(item)

        to_confirm = getattr(item, 'valid', '') == None
        to_confirm = to_confirm and u'tarif-to-confirm' or u''

        elements = [self.render_field(item, 'min', after=u' €', to_confirm=to_confirm),
                    self.render_field(item, 'max', after=u' €', before=' / ', to_confirm=to_confirm),
                    self.render_field(item, 'cmt', to_confirm=to_confirm)]
        return u''.join(elements)

    def render_field(self, item, attr, before=u'', after=u'', to_confirm=u''):
        subtypes = getattr(self.table, 'tarif_{0}_subtypes'.format(attr))
        if item.subtype not in subtypes:
            return u''

        value = getattr(item, attr, '') or ''
        input_text = (u'{0}<input type="text" class="tarif-{1}-input {2}"'
                      u'name="tarif_{1}_{3}_{4}" value="{5}"/>{6}')
        return input_text.format(before, attr, to_confirm, item.type, item.subtype,
                                 value, after)


class TarifEditionColumnInputsManager(TarifEditionColumnInputsMixin, grok.MultiAdapter):
    grok.adapts(zope.interface.Interface,
                zope.interface.Interface,
                interfaces.ITarifEditionManager)
    grok.name('inputs')
    header = u''
    weight = 60

    def get_item(self, item):
        return item


class TarifEditionColumnInputsToConfirm(TarifEditionColumnInputsMixin, grok.MultiAdapter):
    grok.adapts(zope.interface.Interface,
                zope.interface.Interface,
                interfaces.ITarifEditionToConfirm)
    grok.name('inputs')
    header = u''
    weight = 60

    def get_item(self, item):
        # Get tarif to confirm values
        type = getattr(item, 'type', '')
        subtype = getattr(item, 'subtype', '')
        if not type and not subtype:
            return u''

        to_confirm_item = Tarifs.get_hebergement_tarif_to_confirm(self.table.heb_pk, type, subtype)
        # Replace tarif to tarif_to_confirm if exists
        item = to_confirm_item and to_confirm_item or item
        return item
