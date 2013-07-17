# encoding: utf-8
"""
gites.core

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

import sqlalchemy as sa

import zope.component
import zope.interface
import zope.publisher
from five import grok

from z3c.table import column, interfaces as table_interfaces, table, value
from zope.i18n import translate

from affinitic.db.cache import FromCache
from gites.db import content as mappers, session
from gites.locales import GitesMessageFactory as _

from gites.core import interfaces


class HebComparisonTable(table.Table):
    zope.interface.implements(interfaces.IHebergementComparisonTable)

    cssClasses = {'table': 'z3c-listing percent100 listing nosort comparison'}
    cssClassEven = u'odd'
    cssClassOdd = u'even'
    sortOn = None
    startBatchingAt = 9999

    def __init__(self, context, request, heb_pks):
        super(HebComparisonTable, self).__init__(context, request)
        self.heb_pks = heb_pks

    def update(self):
        """ Adds css classes for the hosting type """
        super(HebComparisonTable, self).update()
        query = session().query(mappers.Hebergement.heb_pk,
                                mappers.TypeHebergement.type_heb_code)
        query = query.join('type')
        query = query.filter(mappers.Hebergement.heb_pk.in_(self.heb_pks))
        query = query.order_by(mappers.Hebergement.heb_pk)
        for idx, hosting in enumerate(query.all()):
            column = self.columns[idx + 1]
            classes = [self._hosting_type(hosting.type_heb_code)]
            if column.cssClasses.get('td'):
                classes.append(column.cssClasses.get('td'))
            column.cssClasses['td'] = ' '.join(classes)

    def _hosting_type(self, host_type):
        if host_type not in ('CH', 'MH', 'CHECR'):
            return 'gites'
        return 'chambres'

    @property
    def values(self):
        """ Returns the values for an hosting """
        adapter = zope.component.getMultiAdapter(
            (self.context, self.request, self), table_interfaces.IValues)
        return adapter.values

    def renderRow(self, row, css_class):
        """
        Override of the renderRow method to add some css on the header rows
        """
        if not row[0][0].get('description'):
            self.cssClasses['tr'] = 'header'
        else:
            self.cssClasses['tr'] = ''
        return super(HebComparisonTable, self).renderRow(row, css_class)


class ComparisonList(object):

    def __init__(self, *elements):
        self._columns = list(elements)
        self._types = [None]

    def add_element(self, *elements):
        for element in elements:
            self._columns.append(element)

    def keys(self):
        return [e.key for e in self._columns]

    def add_type(self, type):
        self._types.append(type)

    @property
    def columns(self):
        return [c for c in self._columns if c.type in self._types]

    def get_columns(self, table=None):
        columns = [e for e in self._columns if e.type in self._types]
        if table is not None:
            columns = [e for e in columns if e.table == table]
        return columns

    def get_columns_keys(self, table=None):
        return [e.key for e in self.get_columns(table=table)]


class ComparisonColumn(object):

    def __init__(self, key, translation, table=None, type=None):
        self.key = key
        self.table = table
        self.translation = translation
        self.type = type


class HebComparisonValues(value.ValuesMixin,
                          grok.MultiAdapter):
    grok.provides(table_interfaces.IValues)
    grok.adapts(zope.interface.Interface,
                zope.publisher.interfaces.browser.IBrowserRequest,
                interfaces.IHebergementComparisonTable)

    heb_add_columns = ['heb_code_gdw', 'heb_cgt_cap_min', 'heb_cgt_cap_max',
                       'heb_pk', 'heb_calendrier_proprio']

    def translate(self, msgid):
        return translate(_(msgid), target_language=self.language)

    @property
    def _base_comparison_list(self):
        return ComparisonList(
            ComparisonColumn(u'heb_nom', u'', table='hebergement'),
            ComparisonColumn(u'picture', u''),
            ComparisonColumn(u'heb_nombre_epis',
                             u'%s / %s' % (self.translate('Epis'),
                                           self.translate('Cles')),
                             table='epis'),
            ComparisonColumn(u'capacity', self.translate('capacite')),
            ComparisonColumn(u'heb_cgt_nbre_chmbre',
                             self.translate('Chambres'),
                             table='hebergement'),
            ComparisonColumn(u'heb_tarif_we_bs',
                             u'%s (%s)' % (self.translate('basse_saison'),
                                           self.translate('week-end')),
                             table='hebergement',
                             type='gites'),
            ComparisonColumn(u'heb_tarif_sem_bs',
                             self.translate('basse_saison'),
                             table='hebergement',
                             type='gites'),
            ComparisonColumn(u'heb_tarif_we_ms',
                             u'%s (%s)' % (self.translate('moyenne_saison'),
                                           self.translate('week-end')),
                             table='hebergement',
                             type='gites'),
            ComparisonColumn(u'heb_tarif_sem_ms',
                             self.translate('moyenne_saison'),
                             table='hebergement',
                             type='gites'),
            ComparisonColumn(u'heb_tarif_we_hs',
                             u'%s (%s)' % (self.translate('haute_saison'),
                                           self.translate('week-end')),
                             table='hebergement',
                             type='gites'),
            ComparisonColumn(u'heb_tarif_sem_hs',
                             self.translate('haute_saison'),
                             table='hebergement',
                             type='gites'),
            ComparisonColumn(u'heb_tarif_we_3n', self.translate('3_nuits'),
                             table='hebergement',
                             type='gites'),
            ComparisonColumn(u'heb_tarif_we_4n', self.translate('4_nuits'),
                             table='hebergement',
                             type='gites'),
            ComparisonColumn(u'heb_tarif_semaine_fin_annee',
                             self.translate('fin_d_annee'),
                             table='hebergement',
                             type='gites'),
            ComparisonColumn(u'heb_tarif_garantie', self.translate('garantie'),
                             table='hebergement',
                             type='gites'),
            ComparisonColumn(u'heb_tarif_chmbr_avec_dej_1p',
                             u'%s (%s)' % (self.translate('nuit_avec_petit_dejeuner'),
                                           self.translate('1_p')),
                             table='hebergement',
                             type='chambres'),
            ComparisonColumn(u'heb_tarif_chmbr_avec_dej_2p',
                             u'%s (%s)' % (self.translate('nuit_avec_petit_dejeuner'),
                                           self.translate('2_p')),
                             table='hebergement',
                             type='chambres'),
            ComparisonColumn(u'heb_tarif_chmbr_avec_dej_3p',
                             u'%s (%s)' % (self.translate('nuit_avec_petit_dejeuner'),
                                           self.translate('p_plus')),
                             table='hebergement',
                             type='chambres'),
            ComparisonColumn(u'heb_tarif_chmbr_sans_dej_1p',
                             u'%s (%s)' % (self.translate('deduction_si_pas_petit_dejeuner'),
                                           self.translate('1_p')),
                             table='hebergement',
                             type='chambres'),
            ComparisonColumn(u'heb_tarif_chmbr_sans_dej_2p',
                             u'%s (%s)' % (self.translate('deduction_si_pas_petit_dejeuner'),
                                           self.translate('2_p')),
                             table='hebergement',
                             type='chambres'),
            ComparisonColumn(u'heb_tarif_chmbr_sans_dej_3p',
                             u'%s (%s)' % (self.translate('deduction_si_pas_petit_dejeuner'),
                                           self.translate('p_plus')),
                             table='hebergement',
                             type='chambres'),
            ComparisonColumn(u'heb_table_hote',
                             self.translate('table_hotes'),
                             type='chambres'),
            ComparisonColumn(u'heb_tarif_chmbr_table_hote_1p',
                             u'%s (%s)' % (self.translate('table_hotes'),
                                           self.translate('tarif')),
                             table='hebergement',
                             type='chambres'),
            ComparisonColumn(u'heb_taxe_montant',
                             self.translate('taxe_sejour'),
                             table='hebergement'),
            ComparisonColumn(u'pro_langue', self.translate('langue'),
                             table='proprio'))

    @property
    def values(self):
        self.language = self.request.get('LANGUAGE', 'fr')
        self.comparison_list = self._base_comparison_list

        for heb_type in self.heb_types:
            self.comparison_list.add_type(heb_type)
        self.add_metadata_columns()
        self.comparison_list.add_element(ComparisonColumn(
            u'calendar', _('calendrier')))
        self.heb_columns = self.comparison_list.get_columns_keys('hebergement')

        return self.rows_to_cols(self.rows)

    @property
    def rows(self):
        results = []
        for result in self.query.all():
            criteria = {}
            # Hebergement columns
            for c in self.heb_columns:
                criteria[c] = getattr(result, c)
            # Metadatas columns
            criteria.update(self.get_metadatas(result.heb_pk))
            # Calculated columns
            criteria['heb_nombre_epis'] = result.heb_nombre_epis
            criteria['heb_table_hote'] = self.get_table_hote(result.heb_pk)
            if result.heb_cgt_cap_min != result.heb_cgt_cap_max:
                criteria['capacity'] = u'%s/%s' % (result.heb_cgt_cap_min,
                                                   result.heb_cgt_cap_max)
            else:
                criteria['capacity'] = result.heb_cgt_cap_max
            criteria['pro_langue'] = result.pro_langue
            criteria['picture'] = u'<img width="181" height="115" ' \
                'src="%s/photos_heb/%s00.jpg" />' % (self.context.portal_url(),
                                                     result.heb_code_gdw)
            criteria['calendar'] = self.translate(
                'desoles_pas_de_calendrier_pour_ce_gite')
            if result.heb_calendrier_proprio == 'actif':
                criteria['calendar'] = u'<div id="description-calendrier">' \
                    u'<div id="calendars%s"></div><input type="hidden" ' \
                    u'id="reset" /><input type="hidden" name="start" ' \
                    u'value="" id="start" /><input type="hidden" name="end" ' \
                    u'value="" id="end" /></div>' % result.heb_pk
            results.append(criteria)
        return results

    @property
    def heb_types(self):
        query = session().query(mappers.Hebergement.heb_pk,
                                mappers.TypeHebergement.type_heb_code)
        query = query.options(FromCache('gdw'))
        query = query.join('type')
        query = query.filter(
            mappers.Hebergement.heb_pk.in_(self.table.heb_pks))
        return [self.table._hosting_type(h.type_heb_code) for h in query.all()]

    @property
    def query(self):
        query = session().query(mappers.Proprio.pro_langue,
                                mappers.TypeHebergement.type_heb_code,
                                mappers.LinkHebergementEpis.heb_nombre_epis)
        query = query.options(FromCache('gdw'))
        query = query.join('hebergements', 'type').outerjoin('hebergements', 'epis')
        for c in self.heb_columns + self.heb_add_columns:
            query = query.add_column(getattr(mappers.Hebergement, c))
        query = query.filter(
            mappers.Hebergement.heb_pk.in_(self.table.heb_pks))
        return query.order_by(mappers.Hebergement.heb_pk)

    def add_metadata_columns(self):
        query = session().query(mappers.Metadata).filter(
            mappers.Metadata.met_filterable == True)
        query = query.order_by(mappers.Metadata.metadata_type_id)
        for metadata in query.all():
            self.comparison_list.add_element(ComparisonColumn(
                u'met_%s' % metadata.met_pk, metadata.getTitre(self.language)))

    def get_metadatas(self, heb_pk):
        """ Adds the metadatas for the given heb pk """
        query = session().query(mappers.LinkHebergementMetadata.metadata_fk,
                                mappers.LinkHebergementMetadata.link_met_value)
        query = query.join('metadata_info')
        query = query.filter(sa.and_(
            mappers.LinkHebergementMetadata.heb_fk == heb_pk,
            mappers.Metadata.met_filterable == True))
        return dict([('met_%s' % m.metadata_fk, m.link_met_value) for m \
                     in query.all()])

    def get_table_hote(self, heb_pk):
        """ Returns the host tables metadatas for the given heb pk """
        query = session().query(mappers.LinkHebergementMetadata)
        query = query.join('metadata_info')
        query = query.filter(sa.and_(
            mappers.LinkHebergementMetadata.heb_fk == heb_pk,
            mappers.LinkHebergementMetadata.link_met_value == True,
            mappers.Metadata.met_id.in_(['heb_tabhot_repas_familial',
                                         'heb_tabhot_gourmand',
                                         'heb_tabhot_gastronomique'])))
        result = query.first()
        if result:
            return result.metadata_info.getTitre(self.language)

    def rows_to_cols(self, values):
        """ Converts the rows to columns """
        new_values = []
        for column in self.comparison_list.columns:
            column_values = {'description': column.translation}
            for idx, row in enumerate(values):
                column_values['col_%s' % str(idx + 1)] = row[column.key]
            new_values.append(column_values)
        return new_values


class HebComparisonColumn(column.GetAttrColumn):
    """ Base class for the comparison columns """
    grok.provides(table_interfaces.IColumn)
    grok.adapts(zope.interface.Interface,
                zope.interface.Interface,
                interfaces.IHebergementComparisonTable)

    def update(self):
        classes = {'td': 'center'}
        classes['td'] = '%s comparison-%s' % (classes['td'],
                                              str(len(self.table.columns) - 1))
        self.cssClasses = classes

    def renderCell(self, item):
        value = item.get(self.attrName, '')
        if isinstance(value, bool):
            return {True: '<span class="icon true">v</span>',
                    False: '<span class="icon false">x</span>'}[value]
        value = value not in (u'None', u'', u' ') and value or None
        return value or '-'


class HebComparisonTitle(column.GetAttrColumn, grok.MultiAdapter):
    grok.provides(table_interfaces.IColumn)
    grok.adapts(zope.interface.Interface,
                zope.interface.Interface,
                interfaces.IHebergementComparisonTable)
    grok.name('column_title')
    header = u''
    weight = 10

    cssClasses = {'td': 'description'}

    def renderCell(self, item):
        return item.get('description', u'')


class HebComparisonColumnFirst(HebComparisonColumn, grok.MultiAdapter):
    grok.name('column_1')
    header = u''
    attrName = u'col_1'
    weight = 20


class HebComparisonColumnSecond(HebComparisonColumn, grok.MultiAdapter):
    grok.name('column_2')
    header = u''
    attrName = u'col_2'
    weight = 30


class HebComparisonColumnThird(HebComparisonColumn, grok.MultiAdapter):
    grok.adapts(zope.interface.Interface,
                zope.interface.Interface,
                interfaces.IHebergementComparisonThree)
    grok.name('column_3')
    header = u''
    attrName = u'col_3'
    weight = 40


class HebComparisonColumnFourth(HebComparisonColumn, grok.MultiAdapter):
    grok.adapts(zope.interface.Interface,
                zope.interface.Interface,
                interfaces.IHebergementComparisonFour)
    grok.name('column_4')
    header = u''
    attrName = u'col_4'
    weight = 50
