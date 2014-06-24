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
from zope.i18n import translate
from five import grok

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
        heb_pk = self.request.get('heb_pk', None)
        if not heb_pk:
            return []

        heb = Hebergement.first(heb_pk=heb_pk)
        if heb.type.type_heb_type == 'gite':
            tarifs_types = TarifsType.get(gite=True)
        else:
            tarifs_types = TarifsType.get(chambre=True)

        self.tarifs = Tarifs.get_hebergement_tarifs(heb_pk)
        tarifs_table = []
        for tarifs_type in tarifs_types:
            tarifs_table.append(self._get_tarif_line(tarifs_type))
        return tarifs_table

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
    grok.name('values')
    header = u''
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
        input_text = (u'{0}<input type="text" class="tarif-{1}-input"'
                      u'name="tarif_{1}_{2}_{3}" value="{4}"/>{5}')
        return input_text.format(before, attr, item.type, item.subtype, value,
                                 after)
