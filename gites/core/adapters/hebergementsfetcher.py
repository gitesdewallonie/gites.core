# -*- coding: utf-8 -*-
import hashlib
import json
import geoalchemy
from dateutil.relativedelta import relativedelta
import sqlalchemy as sa
from plone.memoize.instance import memoize
from five import grok
from zope.component import getMultiAdapter
from zope.interface import Interface, directlyProvides
from zope.publisher.interfaces.browser import IBrowserRequest
from affinitic.db.cache import FromCache
from Products.Maps.interfaces import IMarker
from gites.db import session
from gites.db.interfaces import ICommune
from gites.db.content import (LinkHebergementMetadata, Hebergement,
                              LinkHebergementEpis, Commune, Proprio,
                              TypeHebergement, ReservationProprio)
from gites.core.interfaces import IHebergementsFetcher, IHebergementInSearch
from Products.CMFPlone.interfaces import IPloneSiteRoot
from gites.core.browser.moteur_recherche import MoteurRecherche
from gites.core.content.interfaces import IPackage
from gites.core.utils import getGeocodedLocation


class BaseHebergementsFetcher(grok.MultiAdapter):
    grok.baseclass()
    grok.implements(IHebergementsFetcher)

    batch_size = 10

    def __init__(self, context, view, request):
        self.context = context
        self.view = view
        self.request = request

    def selected_page(self):
        return int(self.data.get('page', 0))

    @property
    def batch_start(self):
        return self.selected_page() * self.batch_size

    @property
    def batch_end(self):
        return self.batch_start + self.batch_size

    def selected_order(self):
        return self.data.get('sort', 'hebergement')

    @property
    def data(self):
        return self.request.form

    @memoize
    def request_parameters(self):
        return {}
        if self.request._file is None:
            return {}
        request_body = self.request._file.read()
        self.request._file.seek(0)
        try:
            return json.loads(request_body)
        except ValueError:
            return {}

    def selected_keywords(self):
        keywords = self.data.get('keywords[]', [])
        if isinstance(keywords, (str, unicode)):
            keywords = [keywords]
        return keywords

    def selected_classifications(self):
        classes = self.data.get('classification', []) or self.data.get('form.widgets.classification[]', [])
        if isinstance(classes, (str, unicode)):
            classes = [classes]
        return classes

    def __call__(self):
        query = self._query.order_by(*self.order_by())
        query = query.slice(self.batch_start, self.batch_end)
        hebergements = []
        for heb in query.all():
            if isinstance(heb, tuple) and isinstance(heb[0], Hebergement):
                hebergement = heb[0]
                for key in heb.keys()[1:]:
                    value = getattr(heb, key)
                    setattr(hebergement, key, value)
                hebergements.append(hebergement)
            elif isinstance(heb, tuple):
                directlyProvides(heb, IHebergementInSearch)
                hebergements.append(heb)
            else:
                hebergements.append(heb)
        reference = self.data.get('reference')
        if len(hebergements) == 1 and reference and self.selected_page() != 0:
            # if searching by name and finding only one gite, redirect to its
            # description
            hebPk = hebergements[0].heb_pk
            hebergement = session().query(Hebergement).get(hebPk)
            hebURL = getMultiAdapter((hebergement.__of__(self.context.hebergement),
                                      self.request), name="url")
            self.request.response.redirect(str(hebURL))
            return ''
        return hebergements

    def __len__(self):
        count = self._query.count()
        return count

    def order_by(self):
        if self.selected_order() == 'pers_numbers':
            return (Hebergement.heb_cgt_cap_min.asc(), Hebergement.heb_nom)
        elif self.selected_order() == 'room_count':
            return (Hebergement.heb_cgt_nbre_chmbre.asc(), Hebergement.heb_nom)
        elif self.selected_order() == 'epis':
            return (LinkHebergementEpis.heb_nombre_epis.desc(), Hebergement.heb_nom)
        else:
            return (Hebergement.heb_nom, TypeHebergement.type_heb_type)

    @property
    def cookie_key(self):
        """ Returns the cookie key for the current context """
        return hashlib.md5(self.context.absolute_url()).hexdigest()

    def update_cookie_sort(self, value):
        """ Updates the cookie to correctly display the sort value """
        self.request.response.setCookie(
            '%s_sort' % self.cookie_key,
            value)


class PackageHebergementFetcher(BaseHebergementsFetcher):
    grok.adapts(IPackage, Interface, IBrowserRequest)

    def getCriteria(self):
        return self.context.getCriteria()

    @property
    def _query(self):
        point = None
        if hasattr(self.context, 'is_geolocalized') and self.context.is_geolocalized:
            geomarker = IMarker(self.context)
            user_range = self.context.getRange()
            point = 'POINT(%s %s)' % (geomarker.longitude, geomarker.latitude)
            point = geoalchemy.base.WKTSpatialElement(point, srid=3447)
        if point is not None:
            query = session().query(Hebergement,
                                    Hebergement.heb_location.distance_sphere(point).label('distance'),
                                    TypeHebergement.type_heb_code.label('heb_type_code'),
                                    TypeHebergement.type_heb_type.label('heb_type_type')
                                    )
        else:
            query = session().query(Hebergement,
                                    TypeHebergement.type_heb_code.label('heb_type_code'),
                                    TypeHebergement.type_heb_type.label('heb_type_type')
                                    )
        query = query.join('type').join('commune').outerjoin('epis').join('proprio')
        query = query.options(
            FromCache('gdw'))
        subquery = session().query(LinkHebergementMetadata.heb_fk)
        criteria = set()
        criteria.update(
            self.getCriteria(),
            self.selected_keywords())
        if criteria:
            subquery = subquery.filter(LinkHebergementMetadata.metadata_fk.in_(criteria))
            subquery = subquery.filter(LinkHebergementMetadata.link_met_value == True)
            subquery = subquery.group_by(LinkHebergementMetadata.heb_fk)
            subquery = subquery.having(sa.func.count() == len(criteria))
            subquery = subquery.subquery()
            query = query.filter(Hebergement.heb_pk == subquery.c.heb_fk)
        if hasattr(self.context, 'is_geolocalized') and self.context.is_geolocalized:
            query = query.filter(Hebergement.heb_location.distance_sphere(point) < 1000 * user_range)
        query = query.filter(sa.and_(Hebergement.heb_site_public == '1',
                                     Proprio.pro_etat == True))
        return query

    def order_by(self):
        if self.selected_order() == 'pers_numbers':
            return (Hebergement.heb_cgt_cap_min.asc(), Hebergement.heb_nom)
        elif self.selected_order() == 'room_count':
            return (Hebergement.heb_cgt_nbre_chmbre.asc(), Hebergement.heb_nom)
        elif self.selected_order() == 'epis':
            return (LinkHebergementEpis.heb_nombre_epis.desc(), Hebergement.heb_nom)
        elif self.selected_order() == 'heb_type':
            return (TypeHebergement.type_heb_type.desc(), Hebergement.heb_nom)
        elif hasattr(self.context, 'is_geolocalized') and self.context.is_geolocalized:
            self.update_cookie_sort('distance')
            return ('distance', )
        else:
            return ('heb_nom', 'heb_type_type')


class CommuneHebFetcher(BaseHebergementsFetcher):
    grok.adapts(ICommune, Interface, IBrowserRequest)

    @property
    def _query(self):
        query = session().query(Hebergement,
                                TypeHebergement.type_heb_code.label('heb_type_code'),
                                ).join('type').join('commune').outerjoin('epis').join('proprio')
        query = query.options(
            FromCache('gdw'))
        typeHeb = self.context.aq_parent
        query = query.filter(sa.and_(Commune.com_id == self.context.com_id,
                                     Hebergement.heb_typeheb_fk == typeHeb.type_heb_pk))
        query = query.filter(sa.and_(Hebergement.heb_site_public == '1',
                                     Proprio.pro_etat == True))
        return query


class SearchHebFetcher(BaseHebergementsFetcher):
    grok.adapts(Interface, MoteurRecherche, IBrowserRequest)

    def __call__(self):
        hebergements = super(SearchHebFetcher, self).__call__()
        hebergements = self._group_grouped_hebs(hebergements)
        return hebergements

    def _group_grouped_hebs(self, hebergements):
        """
        We want:
            heb1,heb2,heb3,group
        But not:
            heb1,group,heb2,heb3
        """
        position = {}
        heblist = []
        hebgrplist = []
        i = 0
        for hebergement in hebergements:
            if hebergement.heb_groupement_pk != None:
                position[hebergement.heb_groupement_pk] = i
            i += 1
            if hebergement.heb_type == 'gite-groupes':
                hebgrplist.append(hebergement)
            else:
                heblist.append(hebergement)
        if not hebgrplist:
            return hebergements
        for heb in hebgrplist:
            heblist.insert(position[heb.heb_groupement_pk], heb)
        return heblist

    def _get_data_from_form(self):
        from gites.core.browser.search import SearchHostingForm
        form = SearchHostingForm(self.context, self.request)
        form.update()
        data, errors = form.extractData()
        return data

    @property
    @memoize
    def data(self):
        params = super(SearchHebFetcher, self).data
        data = self._get_data_from_form()
        params.update(data)
        return params

    @property
    def is_geolocalized(self):
        return self.geocodedLocation is not None

    @property
    def geocodedLocation(self):
        near_to = self.data.get('nearTo')
        return getGeocodedLocation(near_to, self.request.get('LANGUAGE'))

    def filter_capacity(self, capacityMin, query):
        if capacityMin:
            if capacityMin < 16:
                capacityMax = capacityMin + 4
                query = query.filter(sa.or_(Hebergement.heb_cgt_cap_min.between(capacityMin, capacityMax),
                                            Hebergement.heb_cgt_cap_max.between(capacityMin, capacityMax)))
            else:
                capacityMax = capacityMin
                capacityMin = 16
                query = query.filter(sa.and_(Hebergement.heb_cgt_cap_min >= capacityMin,
                                             Hebergement.heb_cgt_cap_max >= capacityMax))
        return query

    def filter_capacity_in_group(self, capacityMin, query):
        if capacityMin:
            if capacityMin < 16:
                capacityMax = capacityMin + 4
                return '(sum(heb_cgt_cap_min) between %s and %s) \
                        or \
                        (sum(heb_cgt_cap_max) between %s and %s)' % (capacityMin, capacityMax,
                                                                     capacityMin, capacityMax)
            else:
                capacityMax = capacityMin
                capacityMin = 16
                return '(sum(heb_cgt_cap_min) >= %s) \
                        and \
                        (sum(heb_cgt_cap_max) >= %s)' % (capacityMin, capacityMax)

    def filter_heb_type(self, show_gites, show_chambres, query):
        if show_gites:
            return query.filter(TypeHebergement.type_heb_type == 'gite')
        elif show_chambres:
            return query.filter(TypeHebergement.type_heb_type == 'chambre')

    def filter_available_date(self, from_date, to_date, query):
        query = query.filter(Hebergement.heb_calendrier_proprio != 'non actif')
        beginDate = from_date or (to_date + relativedelta(days=-1))
        endDate = to_date or (from_date + relativedelta(days=+1))
        busyHebPks = sa.select([ReservationProprio.heb_fk],
                               sa.and_(ReservationProprio.res_date >= beginDate,
                                       ReservationProprio.res_date < endDate))
        query = query.filter(~Hebergement.heb_pk.in_(busyHebPks))
        return query

    def apply_filters(self, query, group=False):
        reference = self.data.get('reference')
        capacity = self.data.get('capacityMin') or self.data.get('form.widgets.capacityMin')
        heb_type = self.data.get('form.widgets.hebergementType') or self.data.get('form.widgets.hebergementType[]')
        show_gites = heb_type and 'gite-meuble' in heb_type
        show_chambres = heb_type and 'chambre-hote' in heb_type
        from_date = self.data.get('fromDateAvancee') or self.data.get('form.widgets.fromDate')
        to_date = self.data.get('toDateAvancee') or self.data.get('form.widgets.toDate')
        smokers = self.data.get('form.widgets.smokers')
        animals = self.data.get('form.widgets.animals')
        roomAmount = self.data.get('form.widgets.roomAmount')
        classifications = self.selected_classifications()
        #11 = Animal
        #12 = Fumeur
        if animals:
            subquery = session().query(LinkHebergementMetadata.heb_fk)
            subquery = subquery.filter(LinkHebergementMetadata.metadata_fk == 11)
            subquery = subquery.filter(LinkHebergementMetadata.link_met_value == True)
            subquery = subquery.group_by(LinkHebergementMetadata.heb_fk)
            subquery = subquery.subquery()
            query = query.filter(Hebergement.heb_pk == subquery.c.heb_fk)

        if smokers:
            subquery = session().query(LinkHebergementMetadata.heb_fk)
            subquery = subquery.filter(LinkHebergementMetadata.metadata_fk == 12)
            subquery = subquery.filter(LinkHebergementMetadata.link_met_value == True)
            subquery = subquery.group_by(LinkHebergementMetadata.heb_fk)
            subquery = subquery.subquery()
            query = query.filter(Hebergement.heb_pk == subquery.c.heb_fk)

        if classifications:
            query = query.filter(sa.and_(LinkHebergementEpis.heb_nombre_epis.in_(classifications),
                                         Hebergement.heb_pk == LinkHebergementEpis.heb_pk))
        if roomAmount:
            query = query.filter(Hebergement.heb_cgt_nbre_chmbre >= roomAmount)
        if reference:
            reference = reference.strip()
            query = query.filter(sa.or_(sa.func.unaccent(Hebergement.heb_nom).ilike("%%%s%%" % reference),
                                        Hebergement.heb_nom.ilike("%%%s%%" % reference)))
        if show_gites != show_chambres:  # XOR
            query = self.filter_heb_type(show_gites, show_chambres, query)
        if capacity and not group:
            query = self.filter_capacity(capacity, query)
        if from_date or to_date:
            query = self.filter_available_date(from_date, to_date, query)
        query = query.filter(sa.and_(Hebergement.heb_site_public == '1',
                                     Proprio.pro_etat == True))
        return query

    def _query_grouped_heb(self, session):
        if self.geocodedLocation:
            point = 'POINT(%s %s)' % (self.geocodedLocation.coordinates[1],
                                      self.geocodedLocation.coordinates[0])
            point = geoalchemy.base.WKTSpatialElement(point, srid=3447)

            query = session.query(
                sa.func.min(Hebergement.heb_nom).label('heb_nom'),
                sa.func.avg(Hebergement.heb_location.distance_sphere(point)).label('distance'),
                sa.func.sum(Hebergement.heb_cgt_nbre_chmbre).label('heb_cgt_nbre_chmbre'),
                sa.func.sum(Hebergement.heb_cgt_cap_min).label('heb_cgt_cap_min'),
                sa.func.sum(Hebergement.heb_cgt_cap_max).label('heb_cgt_cap_max'),
                sa.literal_column("'gite-groupes'").label('heb_type'),
                sa.func.min(TypeHebergement.type_heb_type).label('heb_type_type'),
                sa.func.min(TypeHebergement.type_heb_code).label('heb_type_code'),
                sa.func.min(Hebergement.heb_code_gdw).label('heb_code_gdw'),
                sa.func.min(Hebergement.heb_pk).label('heb_pk'),
                sa.func.max(LinkHebergementEpis.heb_nombre_epis).label('heb_nombre_epis'),
                sa.func.min(Hebergement.heb_localite).label('heb_localite'),
                sa.func.min(Hebergement.heb_gps_long).label('heb_gps_long'),
                sa.func.min(Hebergement.heb_gps_lat).label('heb_gps_lat'),
                sa.func.min(Hebergement.heb_groupement_pk).label('heb_groupement_pk'))
        else:
            query = session.query(
                sa.func.min(Hebergement.heb_nom).label('heb_nom'),
                sa.func.sum(Hebergement.heb_cgt_nbre_chmbre).label('heb_cgt_nbre_chmbre'),
                sa.func.sum(Hebergement.heb_cgt_cap_min).label('heb_cgt_cap_min'),
                sa.func.sum(Hebergement.heb_cgt_cap_max).label('heb_cgt_cap_max'),
                sa.literal_column("'gite-groupes'").label('heb_type'),
                sa.func.min(TypeHebergement.type_heb_type).label('heb_type_type'),
                sa.func.min(TypeHebergement.type_heb_code).label('heb_type_code'),
                sa.func.min(Hebergement.heb_code_gdw).label('heb_code_gdw'),
                sa.func.min(Hebergement.heb_pk).label('heb_pk'),
                sa.func.max(LinkHebergementEpis.heb_nombre_epis).label('heb_nombre_epis'),
                sa.func.min(Hebergement.heb_localite).label('heb_localite'),
                sa.func.min(Hebergement.heb_gps_long).label('heb_gps_long'),
                sa.func.min(Hebergement.heb_gps_lat).label('heb_gps_lat'),
                sa.func.min(Hebergement.heb_groupement_pk).label('heb_groupement_pk'))

        query = query.join('proprio').outerjoin('epis').join('type')
        query = query.filter(Hebergement.heb_groupement_pk != None)
        query = self.apply_filters(query, group=True)
        #XXX
        query = query.group_by(Hebergement.heb_groupement_pk)

        capacity = self.data.get('capacityMin')
        capacity_filters = self.filter_capacity_in_group(capacity,
                                                         query)
        if capacity_filters:
            query = query.having(sa.and_(capacity_filters,
                                         sa.func.count() > 1))
        else:
            query = query.having(sa.func.count() > 1)
        return query

    def _query_non_grouped_heb(self, session):
        if self.geocodedLocation:
            point = 'POINT(%s %s)' % (self.geocodedLocation.coordinates[1],
                                      self.geocodedLocation.coordinates[0])
            point = geoalchemy.base.WKTSpatialElement(point, srid=3447)

            query = session.query(
                Hebergement.heb_nom.label('heb_nom'),
                Hebergement.heb_location.distance_sphere(point).label('distance'),
                Hebergement.heb_cgt_nbre_chmbre.label('heb_cgt_nbre_chmbre'),
                Hebergement.heb_cgt_cap_min.label('heb_cgt_cap_min'),
                Hebergement.heb_cgt_cap_max.label('heb_cgt_cap_max'),
                TypeHebergement.type_heb_id.label('heb_type'),
                TypeHebergement.type_heb_type.label('heb_type_type'),
                TypeHebergement.type_heb_code.label('heb_type_code'),
                Hebergement.heb_code_gdw.label('heb_code_gdw'),
                Hebergement.heb_pk.label('heb_pk'),
                LinkHebergementEpis.heb_nombre_epis.label('heb_nombre_epis'),
                Hebergement.heb_localite.label('heb_localite'),
                Hebergement.heb_gps_long.label('heb_gps_long'),
                Hebergement.heb_gps_lat.label('heb_gps_lat'),
                Hebergement.heb_groupement_pk.label('heb_groupement_pk'))
        else:
            query = session.query(
                Hebergement.heb_nom.label('heb_nom'),
                Hebergement.heb_cgt_nbre_chmbre.label('heb_cgt_nbre_chmbre'),
                Hebergement.heb_cgt_cap_min.label('heb_cgt_cap_min'),
                Hebergement.heb_cgt_cap_max.label('heb_cgt_cap_max'),
                TypeHebergement.type_heb_id.label('heb_type'),
                TypeHebergement.type_heb_type.label('heb_type_type'),
                TypeHebergement.type_heb_code.label('heb_type_code'),
                Hebergement.heb_code_gdw.label('heb_code_gdw'),
                Hebergement.heb_pk.label('heb_pk'),
                LinkHebergementEpis.heb_nombre_epis.label('heb_nombre_epis'),
                Hebergement.heb_localite.label('heb_localite'),
                Hebergement.heb_gps_long.label('heb_gps_long'),
                Hebergement.heb_gps_lat.label('heb_gps_lat'),
                Hebergement.heb_groupement_pk.label('heb_groupement_pk'))

        query = query.join('proprio').outerjoin('epis').join('type')
        query = self.apply_filters(query)
        return query

    @property
    def _query(self):
        sess = session()
        query = self._query_non_grouped_heb(sess)
        query = query.options(
            FromCache('gdw'))
        return query.union(self._query_grouped_heb(sess))

    def order_by(self):
        if self.selected_order() == 'pers_numbers':
            return ('heb_cgt_cap_min asc', 'heb_nom')
        elif self.selected_order() == 'room_count':
            return (Hebergement.heb_cgt_nbre_chmbre.asc(), Hebergement.heb_nom)
        elif self.selected_order() == 'epis':
            return (LinkHebergementEpis.heb_nombre_epis.desc(), Hebergement.heb_nom)
        elif self.is_geolocalized:
            self.update_cookie_sort('distance')
            return ('distance', )
        else:
            return ('heb_nom', 'heb_type_type')

    def __len__(self):
        return len(self._query.all())


class SearchHebFetcherOnRoot(SearchHebFetcher):
    grok.adapts(IPloneSiteRoot, Interface, IBrowserRequest)


from gites.core.interfaces import ISearch


class AdvancedSearchHebergementFetcher(PackageHebergementFetcher, SearchHebFetcher):
    grok.adapts(ISearch, Interface, IBrowserRequest)

    def getCriteria(self):
        return []

    __call__ = PackageHebergementFetcher.__call__

    @property
    def _query(self):
        query = PackageHebergementFetcher._query.fget(self)
        return self.apply_filters(query)

    @memoize
    def getCommuneForLocalite(self, localite):
        query = session().query(Commune.com_nom)
        query = query.join('relatedHebergement')
        query = query.options(FromCache('gdw'))
        query = query.filter(Hebergement.heb_localite == localite)
        query = query.limit(1)
        return query.scalar()

    def apply_filters(self, query, group=False):
        query = super(AdvancedSearchHebergementFetcher, self).apply_filters(query, group)
        location = self.data.get('form.widgets.nearTo')
        if location:
            location = self.getCommuneForLocalite(location) or location
            query = query.join('commune')
            query = query.filter(Commune.com_nom == location)
        return query
