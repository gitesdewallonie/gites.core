# -*- coding: utf-8 -*-
from five import grok
from zope import interface

grok.templatedir('templates')
grok.context(interface.Interface)


class ProduitPackageViewletManager(grok.ViewletManager):
    grok.name('gites.produitpackage')

class ProduitPackageViewlet(grok.Viewlet):
    pass

# register all viewlets in this viewlet manager:
grok.viewletmanager(ProduitPackageViewletManager)
