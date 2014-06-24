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
from five import grok

from z3c.table import column, interfaces as table_interfaces, table, value

from gites.core import interfaces
from gites.db.content import Tarifs, TarifsType, Hebergement

TARIF_MIN_SUBTYPES = [
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

TARIF_MAX_SUBTYPES = [
    'WEEK',
    'WEEKEND',
    '3_NIGHTS',
    '4_NIGHTS',
    'END_OF_YEAR',
]

TARIF_CMT_SUBTYPES = [
    'ACCORDING_TO_CONSUMPTION',
    'INCLUDED',
    'INCLUSIVE',
    'TABLE_HOTES',
    'OTHER',
    'SOJOURN_TAX',
]


class TarifEditionTable(table.Table):
    zope.interface.implements(interfaces.ITarifEditionTable)

    cssClasses = {'table': 'z3c-listing percent100 listing nosort'}
    cssClassEven = u'odd'
    cssClassOdd = u'even'
    sortOn = None
    startBatchingAt = 9999

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


class TarifEditionColumnType(TarifEditionColumn, grok.MultiAdapter):
    grok.name('type')
    header = u'Type'
    attrName = u'type'
    weight = 10


class TarifEditionColumnSubtype(TarifEditionColumn, grok.MultiAdapter):
    grok.name('subtype')
    header = u'Sous-Type'
    attrName = u'subtype'
    weight = 20


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


class TarifEditionColumnMin(TarifEditionColumn, grok.MultiAdapter):
    grok.name('min')
    header = u'Minimum'
    attrName = u'min'
    weight = 50

    def renderCell(self, item):
        subtype = getattr(item, 'subtype')
        if subtype not in TARIF_MIN_SUBTYPES:
            return u''

        min = getattr(item, 'min', '') or ''

        render = u"""<input type="text" class="tarif-min-input" name="tarif_min_{0}_{1}" value="{2}"/>""".format(item.type, item.subtype, min)
        return render


class TarifEditionColumnMax(TarifEditionColumn, grok.MultiAdapter):
    grok.name('max')
    header = u'Maximum'
    attrName = u'max'
    weight = 60

    def renderCell(self, item):
        subtype = getattr(item, 'subtype')
        if subtype not in TARIF_MAX_SUBTYPES:
            return u''

        max = getattr(item, 'max', '') or ''

        render = u"""<input type="text" class="tarif-max-input" name="tarif_max_{0}_{1}" value="{2}"/>""".format(item.type, item.subtype, max)
        return render


class TarifEditionColumnCmt(TarifEditionColumn, grok.MultiAdapter):
    grok.name('cmt')
    header = u'Commentaire'
    attrName = u'cmt'
    weight = 70

    def renderCell(self, item):
        subtype = getattr(item, 'subtype')
        if subtype not in TARIF_CMT_SUBTYPES:
            return u''

        cmt = getattr(item, 'cmt', '') or ''

        render = u"""<input type="text" name="tarif_cmt_{0}_{1}" value="{2}"/>""".format(item.type, item.subtype, cmt)
        return render
