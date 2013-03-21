# -*- coding: utf-8 -*-
import json
from sqlalchemy import func
from plone.memoize.instance import memoize
from five import grok
from sqlalchemy.orm import joinedload
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from affinitic.db.cache import FromCache
from gites.db import session
from gites.db.content import LinkHebergementMetadata, Hebergement
from gites.core.interfaces import IHebergementsFetcher
from gites.core.content.interfaces import IPackage


class BaseHebergementsFetcher(grok.MultiAdapter):
    grok.baseclass()
    grok.implements(IHebergementsFetcher)

    def __init__(self, context, view, request):
        self.context = context
        self.view = view
        self.request = request


class PackageHebergementFetcher(BaseHebergementsFetcher):
    grok.adapts(IPackage, Interface, IBrowserRequest)

    @memoize
    def request_filters(self):
        request_body = self.request._file.read()
        self.request._file.seek(0)
        try:
            data = json.loads(request_body)
        except ValueError:
            return []
        return [key for key, value in data.get('data', {}).items() if value is True]

    @property
    def _query(self):
        query = session().query(Hebergement)
        query = query.options(
            joinedload('type', innerjoin=True),
            joinedload('commune', innerjoin=True),
            joinedload('epis', innerjoin=True),
            FromCache('gdw'))
        subquery = session().query(LinkHebergementMetadata.heb_fk)
        criteria = set()
        criteria = criteria.union(
            self.context.getCriteria(),
            self.request_filters())
        subquery = subquery.filter(LinkHebergementMetadata.metadata_fk.in_(criteria))
        subquery = subquery.filter(LinkHebergementMetadata.link_met_value == True)
        subquery = subquery.group_by(LinkHebergementMetadata.heb_fk)
        subquery = subquery.having(func.count() == len(criteria))
        subquery = subquery.subquery()
        query = query.filter(Hebergement.heb_pk == subquery.c.heb_fk)
        return query

    def __len__(self):
        count = self._query.count()
        return count

    def __call__(self):
        return self._query.all()
