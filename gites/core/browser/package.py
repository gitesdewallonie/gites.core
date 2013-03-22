# -*- coding: utf-8 -*-
from five import grok
from zope.interface import implements
from gites.core.content.interfaces import IPackage
from .interfaces import IPackageView
grok.templatedir('templates')


class Package(grok.View):
    """
    View on Idee Sejour
    """
    implements(IPackageView)
    grok.context(IPackage)
    grok.name('package_view')
    grok.require('zope2.View')
