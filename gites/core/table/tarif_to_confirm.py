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


class TarifToConfirmTable(table.Table):
    zope.interface.implements(interfaces.ITarifToConfirmTable)

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


class TarifToConfirmValues(value.ValuesMixin,
                           grok.MultiAdapter):
    grok.provides(table_interfaces.IValues)
    grok.adapts(zope.interface.Interface,
                zope.publisher.interfaces.browser.IBrowserRequest,
                interfaces.ITarifToConfirmTable)

    @property
    def values(self):
        return Tarifs.get_tarifs_to_confirm()


class TarifToConfirmColumn(column.GetAttrColumn):
    """ Base class for the comparison columns """
    grok.provides(table_interfaces.IColumn)
    grok.adapts(zope.interface.Interface,
                zope.interface.Interface,
                interfaces.ITarifToConfirmTable)


class TarifToConfirmColumnHebPk(TarifToConfirmColumn, grok.MultiAdapter):
    grok.name('heb_pk')
    header = u'Pk hébergement'
    attrName = u'heb_pk'
    weight = 10


class TarifToConfirmColumnButton(TarifToConfirmColumn, grok.MultiAdapter):
    grok.name('button')
    header = u'Go'
    weight = 20

    def renderCell(self, item):
        value = getattr(item, 'heb_pk', '') or ''
        render = """
            <form method="GET" action="tarif-edition">
              <input type="hidden" name="heb_pk" value="{0}" />
              <input type="hidden" name="to_confirm" value="1" />
              <input type="submit" value="Go">
            </form>""".format(value)
        return render
