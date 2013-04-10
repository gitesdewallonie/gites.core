# -*- coding: utf-8 -*-
import json
import geoalchemy
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
                              LinkHebergementEpis, Commune, Proprio)
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
        return query.all()

    def __len__(self):
        count = self._query.count()
        return count

    def order_by(self):
        if self.selected_order() == 'pers_numbers':
            return (Hebergement.heb_cgt_cap_max.desc(), Hebergement.heb_nom)
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
        query = session().query(Hebergement).join('type').join('commune').join('epis')
        query = query.options(
            FromCache('gdw'))
        subquery = session().query(LinkHebergementMetadata.heb_fk)
        criteria = set()
        criteria = criteria.union(
            self.context.getCriteria(),
            self.selected_keywords())
        subquery = subquery.filter(LinkHebergementMetadata.metadata_fk.in_(criteria))
        subquery = subquery.filter(LinkHebergementMetadata.link_met_value == True)
        subquery = subquery.group_by(LinkHebergementMetadata.heb_fk)
        subquery = subquery.having(sa.func.count() == len(criteria))
        subquery = subquery.subquery()
        query = query.filter(Hebergement.heb_pk == subquery.c.heb_fk)
        if self.context.is_geolocalized():
            geomarker = IMarker(self.context)
            user_range = self.context.getRange()
            point = 'POINT(%s %s)' % (geomarker.longitude, geomarker.latitude)
            point = geoalchemy.base.WKTSpatialElement(point, srid=3447)
            query = query.filter(Hebergement.heb_location.distance_sphere(point) < 1000 * user_range)
        return query

    def order_by(self):
        if self.selected_order() == 'pers_numbers':
            return (Hebergement.heb_cgt_cap_max.desc(), Hebergement.heb_nom)
        elif self.selected_order() == 'room_count':
            return (Hebergement.heb_cgt_nbre_chmbre.desc(), Hebergement.heb_nom)
        elif self.selected_order() == 'epis':
            return (LinkHebergementEpis.heb_nombre_epis.desc(), Hebergement.heb_nom)
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

    @property
    def _query(self):
        reference = self.data.get('reference')
        query = session().query(Hebergement).join('proprio').join('epis')
        query = query.options(
            FromCache('gdw'))
        query = query.filter(Hebergement.heb_nom.ilike("%%%s%%" % reference))
        query = query.filter(sa.and_(Hebergement.heb_site_public == '1',
                                     Proprio.pro_etat == True))
        return query


class SearchHebFetcherOnRoot(SearchHebFetcher):
    grok.adapts(IPloneSiteRoot, Interface, IBrowserRequest)
