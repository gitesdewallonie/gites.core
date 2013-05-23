# encoding: utf-8
"""
gites.core

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

import zope.interface
from five import grok

from gites.core import interfaces
from gites.core.table import hebcomparison


class HebComparisonView(grok.View):
    grok.context(zope.interface.Interface)
    grok.name(u'hebergement-comparison')
    grok.require('zope2.View')
    grok.template('hebcomparison')

    def get_table(self):
        """ Returns the render of the table """
        table = hebcomparison.HebComparisonTable(self.context,
                                                 self.request)
        if len(self.request.get('heb_pk')) == 3:
            zope.interface.alsoProvides(
                table, interfaces.IHebergementComparisonThree)
        elif len(self.request.get('heb_pk')) == 4:
            zope.interface.alsoProvides(
                table, interfaces.IHebergementComparisonFour)
        table.update()
        return table.render()
