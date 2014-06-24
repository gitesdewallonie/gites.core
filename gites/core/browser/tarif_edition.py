# encoding: utf-8
"""
gites.pivot.core

Created by schminitz
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

from datetime import datetime

import zope.interface
from five import grok
from plone import api

from gites.core.table import tarif_edition
from gites.db.content import Tarifs, TarifsType


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
        heb_pk = form.get('tarif_heb_pk', None)
        tarifs_types = TarifsType.get()
        for tt in tarifs_types:
            min = form.get('tarif_min_{0}_{1}'.format(tt.type, tt.subtype), None)
            max = form.get('tarif_max_{0}_{1}'.format(tt.type, tt.subtype), None)
            cmt = form.get('tarif_cmt_{0}_{1}'.format(tt.type, tt.subtype), None)

            # XXX that condition depend on type/subtype
            if min and max:
                self._update_tarif(heb_pk,
                                   tt.type,
                                   tt.subtype,
                                   min,
                                   max,
                                   cmt)

    @staticmethod
    def _update_tarif(heb_pk, type, subtype, min, max, cmt):
        """
        Verify that the values in DB are different then insert new line
        """
        exist = Tarifs.exists_tarifs(heb_pk=heb_pk,
                                     type=type,
                                     subtype=subtype,
                                     min=min,
                                     max=max,
                                     cmt=cmt)
        if not exist:
            # Insert new tarifs line
            tarif = Tarifs(heb_pk=heb_pk,
                           type=type,
                           subtype=subtype,
                           min=min,
                           max=max,
                           cmt=cmt,
                           date=datetime.now(),
                           user=api.user.get_current().id,
                           valid=True)
            tarif.add()
