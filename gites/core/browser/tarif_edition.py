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
from gites.db.content import TarifsType


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

    def update(self):
        """ Apply tarifs changes """
        form = self.request.form
        tarifs_types = TarifsType.get()
        for tt in tarifs_types:
            min = form.get('tarif_min_{0}_{1}'.format(tt.type, tt.subtype), None)
            max = form.get('tarif_max_{0}_{1}'.format(tt.type, tt.subtype), None)
            if min and max:
                # vérifier que c'est different aux données DB et les insérer
                pass
