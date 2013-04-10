# -*- coding: utf-8 -*-
import random
from five import grok
from zope import interface
from Products.CMFCore.utils import getToolByName

grok.templatedir('templates')
grok.context(interface.Interface)


class ProduitPackageViewletManager(grok.ViewletManager):
    grok.name('gites.produitpackage')


class ProduitPackageViewlet(grok.Viewlet):

    def getCarouselPackages(self):
        cat = getToolByName(self.context, 'portal_catalog')
        packages = cat.searchResults(portal_type='Package')
        results = []
        for brain in packages:
            package = brain.getObject()
            showInCarousel = getattr(package, 'showInCarousel', False)
            if showInCarousel:
                results.append(package)
        random.shuffle(results)
        return results


# register all viewlets in this viewlet manager:
grok.viewletmanager(ProduitPackageViewletManager)
