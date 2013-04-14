# -*- coding: utf-8 -*-
from datetime import datetime
import json
import geoalchemy
from dateutil.relativedelta import relativedelta
import sqlalchemy as sa
from plone.memoize.instance import memoize
from five import grok
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from affinitic.db.cache import FromCache
from Products.Maps.interfaces import IMarker
from gites.db import session
from gites.db.interfaces import ICommune
from gites.db.content import (LinkHebergementMetadata, Hebergement,
                              LinkHebergementEpis, Commune, Proprio,
                              TypeHebergement, ReservationProprio)
from gites.core.interfaces import IHebergementsFetcher
from Products.CMFPlone.interfaces import IPloneSiteRoot
from gites.core.browser.moteur_recherche import MoteurRecherche
from gites.core.content.interfaces import IPackage


class BaseHebergementsFetcher(grok.MultiAdapter):
    grok.baseclass()
    grok.implements(IHebergementsFetcher)

    batch_size = 10

    def __init__(self, context, view, request):
        self.context = context
        self.view = view
        self.request = request

    def selected_page(self):
        request_params = self.request_parameters()
        return request_params.get('page', 0)

    @property
    def batch_start(self):
        return self.selected_page() * self.batch_size

    @property
    def batch_end(self):
        return self.batch_start + self.batch_size

    @memoize
    def selected_order(self):
        request_params = self.request_parameters()
        return request_params.get('sort', 'hebergement')

    @memoize
    def request_parameters(self):
        if self.request._file is None:
            return {}
        request_body = self.request._file.read()
        self.request._file.seek(0)
        try:
            return json.loads(request_body)
        except ValueError:
            return {}

    @property
    @memoize
    def data(self):
        params = self.request_parameters()
        params.update(self.request.form.items())
        return params

    def selected_keywords(self):
        data = self.request_parameters()
        return [key for key, value in data.get('keywords', {}).items() if value is True]

    def __call__(self):
        query = self._query.order_by(*self.order_by())
        query = query.slice(self.batch_start, self.batch_end)
        hebergements = []
        for heb in query.all():
            if isinstance(heb, tuple):
                hebergement = heb[0]
                for key in heb.keys()[1:]:
                    value = getattr(heb, key)
                    setattr(hebergement, key, value)
                    hebergements.append(hebergement)
            else:
                hebergements.append(heb)
        return hebergements

    def __len__(self):
        count = self._query.count()
        return count

    def order_by(self):
        if self.selected_order() == 'pers_numbers':
            return (Hebergement.heb_cgt_cap_min.desc(), Hebergement.heb_nom)
        elif self.selected_order() == 'room_count':
            return (Hebergement.heb_cgt_nbre_chmbre.desc(), Hebergement.heb_nom)
        elif self.selected_order() == 'epis':
            return (LinkHebergementEpis.heb_nombre_epis.desc(), Hebergement.heb_nom)
        else:
            return (Hebergement.heb_nom, )


class PackageHebergementFetcher(BaseHebergementsFetcher):
    grok.adapts(IPackage, Interface, IBrowserRequest)

    @property
    def _query(self):
        point = None
        if self.context.is_geolocalized():
            geomarker = IMarker(self.context)
            user_range = self.context.getRange()
            point = 'POINT(%s %s)' % (geomarker.longitude, geomarker.latitude)
            point = geoalchemy.base.WKTSpatialElement(point, srid=3447)
        if point is not None:
            query = session().query(Hebergement,
                                    Hebergement.heb_location.distance_sphere(point).label('distance'))
        else:
            query = session().query(Hebergement)
        query = query.join('type').join('commune').join('epis')
        query = query.options(
            FromCache('gdw'))
        subquery = session().query(LinkHebergementMetadata.heb_fk)
        criteria = set()
        criteria = criteria.union(
            self.context.getCriteria(),
            self.selected_keywords())
        if criteria:
            subquery = subquery.filter(LinkHebergementMetadata.metadata_fk.in_(criteria))
            subquery = subquery.filter(LinkHebergementMetadata.link_met_value == True)
            subquery = subquery.group_by(LinkHebergementMetadata.heb_fk)
            subquery = subquery.having(sa.func.count() == len(criteria))
            subquery = subquery.subquery()
            query = query.filter(Hebergement.heb_pk == subquery.c.heb_fk)
        if self.context.is_geolocalized():
            query = query.filter(Hebergement.heb_location.distance_sphere(point) < 1000 * user_range)
        return query

    def order_by(self):
        if self.selected_order() == 'pers_numbers':
            return (Hebergement.heb_cgt_cap_min.desc(), Hebergement.heb_nom)
        elif self.selected_order() == 'room_count':
            return (Hebergement.heb_cgt_nbre_chmbre.desc(), Hebergement.heb_nom)
        elif self.selected_order() == 'epis':
            return (LinkHebergementEpis.heb_nombre_epis.desc(), Hebergement.heb_nom)
        elif self.selected_order() == 'distance':
            return ('distance', )
        else:
            return ()


class CommuneHebFetcher(BaseHebergementsFetcher):
    grok.adapts(ICommune, Interface, IBrowserRequest)

    @property
    def _query(self):
        query = session().query(Hebergement).join('type').join('commune').join('epis').join('proprio')
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

    def filter_heb_type(self, show_gites, show_chambres, query):
        if show_gites:
            return query.filter(TypeHebergement.type_heb_type == 'gites')
        elif show_chambres:
            return query.filter(TypeHebergement.type_heb_type == 'chambre')

    def filter_available_date(self, from_date, to_date, query):
        if from_date:
            from_date = datetime.strptime(from_date, '%d/%m/%Y').date()
        if to_date:
            to_date = datetime.strptime(to_date, '%d/%m/%Y').date()
        query = query.filter(Hebergement.heb_calendrier_proprio != 'non actif')
        beginDate = from_date or (to_date + relativedelta(days=-1))
        endDate = to_date or (from_date + relativedelta(days=+1))
        busyHebPks = sa.select([ReservationProprio.heb_fk],
                               sa.and_(ReservationProprio.res_date >= beginDate,
                                       ReservationProprio.res_date < endDate))
        query = query.filter(~Hebergement.heb_pk.in_(busyHebPks))
        return query

    @property
    def _query(self):
        reference = self.data.get('reference')
        capacity = self.data.get('form.widgets.capacityMin')
        show_gites = 'gite_meuble' in self.data
        show_chambres = 'chambre_hote' in self.data
        from_date = self.data.get('form.widgets.fromDate')
        to_date = self.data.get('form.widgets.toDate')
        query = session().query(Hebergement).join('proprio').join('epis').join('type')
        query = query.options(
            FromCache('gdw'))
        if reference:
            query = query.filter(sa.or_(sa.func.unaccent(Hebergement.heb_nom).ilike("%%%s%%" % reference),
                                        Hebergement.heb_nom.ilike("%%%s%%" % reference)))
        if show_gites != show_chambres:  # XOR
            query = self.filter_heb_type(show_gites, show_chambres, query)
        if capacity:
            query = self.filter_capacity(capacity, query)
        if from_date or to_date:
            query = self.filter_available_date(from_date, to_date, query)
        query = query.filter(sa.and_(Hebergement.heb_site_public == '1',
                                     Proprio.pro_etat == True))
        return query


class SearchHebFetcherOnRoot(SearchHebFetcher):
    grok.adapts(IPloneSiteRoot, Interface, IBrowserRequest)
