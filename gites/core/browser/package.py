# -*- coding: utf-8 -*-
from five import grok
from gites.core.content.interfaces import IPackage
grok.templatedir('templates')


class Package(grok.View):
    """
    View on Idee Sejour
    """
    grok.context(IPackage)
    grok.name('package_view')
    grok.require('zope2.View')
