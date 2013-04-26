# -*- coding: utf-8 -*-
from zope.interface import implements

from collective.opengraph.viewlets import ATMetatags
from collective.opengraph.interfaces import IOpengraphMetatags


class BoutiqueItemATMetatags(ATMetatags):

    implements(IOpengraphMetatags)

    @property
    def title(self):
        return 'Foo'
