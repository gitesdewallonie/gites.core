# -*- coding: utf-8 -*-
from five import grok
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
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

    def __call__(self):
        import pdb;pdb.set_trace()
