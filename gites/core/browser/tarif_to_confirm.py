# encoding: utf-8
"""
gites.pivot.core

Created by schminitz
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""


import zope.interface
from five import grok

from gites.core.table import tarif_to_confirm


class TarifToConfirmView(grok.View):
    grok.context(zope.interface.Interface)
    grok.name(u'tarif-to-confirm')
    grok.require('gdw.ViewAdmin')
    grok.template('tarif_to_confirm')

    def get_table(self):
        """ Returns the render of the table """
        table = tarif_to_confirm.TarifToConfirmTable(
            self.context,
            self.request)
        table.update()
        return table.render()
