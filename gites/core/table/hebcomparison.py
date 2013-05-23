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
from z3c.table import column, interfaces as table_interfaces, table, value
from five import grok

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

    def update(self):
        """ Adds css classes for the hosting type """
        super(HebComparisonTable, self).update()
        query = session().query(mappers.Hebergement.heb_pk,
                                mappers.TypeHebergement.type_heb_code)
        query = query.join('type')
        query = query.filter(
            mappers.Hebergement.heb_pk.in_(self.request.get('heb_pk')))
        query = query.order_by(mappers.Hebergement.heb_pk)
        for idx, hosting in enumerate(query.all()):
            column = self.columns[idx + 1]
            classes = [self._hosting_type(hosting.type_heb_code)]
            if column.cssClasses.get('td'):
                classes.append(column.cssClasses.get('td'))
            column.cssClasses['td'] = ' '.join(classes)

    def _hosting_type(self, host_type):
        if host_type not in ('CH', 'MH', 'CHECR'):
            return 'gite'
        return 'chambre'

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

    def add_element(self, element):
        self._columns.append(element)

    def keys(self):
        return [e.key for e in self._columns]

    @property
    def columns(self):
        return self._columns

    def get_columns(self, table):
        return [e for e in self._columns if e.table == table]

    def get_columns_keys(self, table):
        return [e.key for e in self._columns if e.table == table]


class ComparisonColumn(object):

    def __init__(self, key, translation, table=None):
        self.key = key
        self.table = table
        self.translation = translation


class HebComparisonValues(value.ValuesMixin,
                          grok.MultiAdapter):
    grok.provides(table_interfaces.IValues)
    grok.adapts(zope.interface.Interface,
                zope.publisher.interfaces.browser.IBrowserRequest,
                interfaces.IHebergementComparisonTable)

    @property
    def base_comparison_columns(self):
        return ComparisonList(
            ComparisonColumn(u'heb_nom', u'', table='hebergement'),
            ComparisonColumn(u'picture', u''),
            ComparisonColumn(u'heb_nbre_epis', _('x_epis'),
                             table='hebergement'),
            ComparisonColumn(u'capacity', _('capacite')),
            ComparisonColumn(u'heb_cgt_nbre_chmbre', _('x_chambres'),
                             table='hebergement'),
            ComparisonColumn(u'heb_tarif_we_bs',
                             u'%s (%s)' % (_('basse_saison'), _('week-end')),
                             table='hebergement'),
            ComparisonColumn(u'heb_tarif_sem_bs', _('basse_saison'),
                             table='hebergement'),
            ComparisonColumn(u'heb_tarif_we_ms',
                             u'%s (%s)' % (_('moyenne_saison'), _('week-end')),
                             table='hebergement'),
            ComparisonColumn(u'heb_tarif_sem_ms', _('moyenne_saison'),
                             table='hebergement'),
            ComparisonColumn(u'heb_tarif_we_hs',
                             u'%s (%s)' % (_('haute_saison'), _('week-end')),
                             table='hebergement'),
            ComparisonColumn(u'heb_tarif_sem_hs', _('haute_saison'),
                             table='hebergement'),
            ComparisonColumn(u'heb_tarif_we_3n', _('3_nuits'),
                             table='hebergement'),
            ComparisonColumn(u'heb_tarif_we_4n', _('4_nuits'),
                             table='hebergement'),
            ComparisonColumn(u'heb_tarif_semaine_fin_annee', _('fin_d_annee'),
                             table='hebergement'),
            ComparisonColumn(u'heb_tarif_garantie', _('garantie'),
                             table='hebergement'),
            ComparisonColumn(u'heb_taxe_montant', _('taxe_sejour'),
                             table='hebergement'),
            ComparisonColumn(u'pro_langue', _('langue'), table='proprio'),)

    @property
    def values(self):
        self.comparison_columns = self.base_comparison_columns
        self.language = self.request.get('LANGUAGE', 'fr')
        self.add_metadata_columns()
        heb_add_columns = ['heb_code_gdw', 'heb_cgt_cap_min',
                           'heb_cgt_cap_max', 'heb_pk']
        heb_columns = self.comparison_columns.get_columns_keys('hebergement')
        query = session().query(mappers.Proprio.pro_langue,
                                mappers.TypeHebergement.type_heb_code)
        query = query.join('hebergements', 'type')
        for c in heb_columns + heb_add_columns:
            query = query.add_column(getattr(mappers.Hebergement, c))
        query = query.filter(
            mappers.Hebergement.heb_pk.in_(self.request.get('heb_pk')))
        query = query.order_by(mappers.Hebergement.heb_pk)

        results = []
        for result in query.all():
            criteria = {}
            # Hebergement columns
            for c in heb_columns:
                criteria[c] = getattr(result, c)
            # Metadatas columns
            criteria.update(self.get_metadatas(result.heb_pk))
            # Calculated columns
            if result.heb_cgt_cap_min != result.heb_cgt_cap_max:
                criteria['capacity'] = u'%s/%s' % (result.heb_cgt_cap_min,
                                                   result.heb_cgt_cap_max)
            else:
                criteria['capacity'] = result.heb_cgt_cap_max
            criteria['pro_langue'] = result.pro_langue
            criteria['picture'] = u'<img width="181" height="115" ' \
                'src="%s/photos_heb/%s00.jpg" />' % (self.context.portal_url(),
                                                     result.heb_code_gdw)
            results.append(criteria)

        return self.rows_to_cols(results)

    def add_metadata_columns(self):
        query = session().query(mappers.Metadata).filter(
            mappers.Metadata.met_filterable == True)
        query = query.order_by(mappers.Metadata.metadata_type_id)
        for metadata in query.all():
            self.comparison_columns.add_element(ComparisonColumn(
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

    def rows_to_cols(self, values):
        """ Converts the rows to columns """
        new_values = []
        for column in self.comparison_columns.columns:
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
        return value


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
