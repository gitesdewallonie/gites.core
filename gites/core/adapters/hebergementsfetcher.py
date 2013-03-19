# -*- coding: utf-8 -*-
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

    @property
    def _query(self):
        query = session().query(Hebergement)
        query = query.options(
            joinedload('type', innerjoin=True),
            joinedload('commune', innerjoin=True),
            joinedload('epis', innerjoin=True),
            FromCache('gdw'))
        subquery = session().query(LinkHebergementMetadata.heb_fk)
        for criterion in self.context.getCriteria():
            is_true = criterion.get('value') == '1'
            subquery = subquery.filter(LinkHebergementMetadata.metadata_fk == criterion.get('criterion'))
            subquery = subquery.filter(LinkHebergementMetadata.link_met_value == is_true)
        subquery = subquery.subquery()
        query = query.filter(Hebergement.heb_pk == subquery.c.heb_fk)
        return query

    def __len__(self):
        return self._query.count()

    def __call__(self):
        return self._query.all()
