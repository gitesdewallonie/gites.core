# encoding: utf-8
"""
gites.pivot.core

Created by schminitz
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

from datetime import datetime

import zope.interface
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from five import grok
from plone import api

from gites.core.table import tarif_edition
from gites.db.content import Tarifs, TarifsType
from gites.locales import GitesMessageFactory as _


class TarifEditionView(grok.View):
    grok.context(zope.interface.Interface)
    grok.name(u'tarif-edition')
    grok.require('cmf.SetOwnPassword')
    grok.template('tarif_edition')

    def get_table(self):
        """ Returns the render of the table """
        table = tarif_edition.TarifEditionTable(
            self.context,
            self.request)
        table.update()
        return table.render()

    def apply_tarifs_changes(self):
        """ Apply tarifs changes """
        form = self.request.form
        heb_pk = form.get('tarif_heb_pk', None)

        if not heb_pk:
            return 1

        # new tarif from proprio are not directly valid
        roles = api.user.get_current().getRoles()
        is_admin = 'Manager' in roles and True or None
        valid = is_admin and True or None

        tarifs_types = TarifsType.get()
        for tt in tarifs_types:
            min = form.get('tarif_min_{0}_{1}'.format(tt.type, tt.subtype))
            max = form.get('tarif_max_{0}_{1}'.format(tt.type, tt.subtype))
            cmt = form.get('tarif_cmt_{0}_{1}'.format(tt.type, tt.subtype))

            # Values are defined and not empty (if not defined: value = None)
            if min != '' and max != '' and cmt != '':
                self._update_tarif(heb_pk,
                                   tt.type,
                                   tt.subtype,
                                   min,
                                   max,
                                   cmt,
                                   valid)
        if is_admin:
            return 1
        else:
            return 2

    @staticmethod
    def _update_tarif(heb_pk, type, subtype, min, max, cmt, valid):
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
                           valid=valid)
            tarif.add()

    def validate(self):
        """
        Validate that tarif_min and tarif_max are float if encoded
        """
        if not self._validate_permission():
            self.error = _(u"Vous n'avez pas les droits d'accéder à cette page.")
            return False

        form = self.request.form
        # Min/Max with value
        for param in [form.get(i) for i in form if ((i.startswith('tarif_max_') or i.startswith('tarif_min_')) and form.get(i))]:
            try:
                float(param)
            except:
                self.error = _(u'Les valeurs pour Minimum et Maximum doivent être des nombres.')
                return False
        return True

    def _validate_permission(self):
        """ User must be Manager or Proprio of heb requested """
        roles = api.user.get_current().getRoles()

        heb_pk = self.request.get('heb_pk', None)
        if 'Manager' in roles:
            return True
        elif 'Proprietaire' in roles:
            proprio_hebs = getUtility(IVocabularyFactory, name='proprio.hebergements')(self.context)
            for proprio_heb in proprio_hebs:
                if proprio_heb.token == heb_pk:
                    return True
        return False
