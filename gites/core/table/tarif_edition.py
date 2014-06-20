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
from gites.db.content import Tarifs


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
        else:
            return Tarifs.get_hebergement_tarifs(heb_pk)


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
        return getattr(item, 'date').strftime('%d-%m-%Y')


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


class TarifEditionColumnMax(TarifEditionColumn, grok.MultiAdapter):
    grok.name('max')
    header = u'Maximum'
    attrName = u'max'
    weight = 60


class TarifEditionColumnCmt(TarifEditionColumn, grok.MultiAdapter):
    grok.name('cmt')
    header = u'Commentaire'
    attrName = u'cmt'
    weight = 70


class TarifEditionColumnValid(TarifEditionColumn, grok.MultiAdapter):
    grok.name('valid')
    header = u'Valide'
    attrName = u'valid'
    weight = 80
