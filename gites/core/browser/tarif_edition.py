# encoding: utf-8
"""
gites.pivot.core

Created by schminitz
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

import zope.interface
from five import grok

from gites.core.table import tarif_edition


class TarifEditionView(grok.View):
    grok.context(zope.interface.Interface)
    grok.name(u'tarif-edition')
    grok.require('gdw.ViewAdmin')
    grok.template('tarif_edition')

    @property
    def heb_pk(self):
        return self.request.get('heb_pk', None)

    def get_table(self):
        """ Returns the render of the table """
        table = tarif_edition.TarifEditionTable(
            self.context,
            self.request)
        table.update()
        return table.render()
