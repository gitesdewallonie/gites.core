# -*- coding: utf-8 -*-
import random
from five import grok
from zope import interface
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName

grok.templatedir('templates')
grok.context(interface.Interface)


class ProduitPackageViewletManager(grok.ViewletManager):
    grok.name('gites.produitpackage')


class ProduitPackageViewlet(grok.Viewlet):

    @memoize
    def getVisualImages(self):
        utool = getToolByName(self.context, 'portal_url')
        portal = utool.getPortalObject()
        carouselFolder = getattr(portal, 'carousel', None)
        if not carouselFolder:
            return []
        currentLanguage = self.request.get('LANGUAGE', 'en')
        cat = getToolByName(self.context, 'portal_catalog')
        path = '/'.join(carouselFolder.getPhysicalPath())
        images = cat.searchResults(portal_type=['Image'],
                                   path={'query': path})
        results = []
        for image in images:
            imageObj = None
            imageLang = ''
            try:
                imageLang = image.getLanguage()
            except AttributeError:
                imageObj = image.getObject()
                imageLang = imageObj.getLanguage()
            if imageLang != '' and imageLang != currentLanguage:
                continue
            if imageObj is None:
                imageObj = image.getObject()
            relatedItems = imageObj.getRelatedItems()
            for relatedItem in relatedItems:
                if relatedItem.portal_type != 'Link':
                    continue
                linkLang = relatedItem.getLanguage()
                if linkLang == '' or linkLang == currentLanguage:
                    visualImage = {'imagesrc': image.getURL(),
                                   'href': relatedItem.remoteUrl,
                                   'title': relatedItem.Title(),
                                   'description': relatedItem.Description()}
                    results.append(visualImage)
        return results

    def getCarouselPackages(self):
        cat = getToolByName(self.context, 'portal_catalog')
        packages = cat.searchResults(portal_type='Package')
        results = []
        for brain in packages:
            package = brain.getObject()
            showInCarousel = getattr(package, 'showInCarousel', False)
            if showInCarousel:
                url = package.absolute_url()
                results.append({'imagesrc': "%s/largePhoto" % url,
                                'href': url,
                                'title': package.Title(),
                                'description': package.Description()})
        return results

    def getCarouselInfos(self):
        results = self.getCarouselPackages() + self.getVisualImages()
        random.shuffle(results)
        return results

# register all viewlets in this viewlet manager:
grok.viewletmanager(ProduitPackageViewletManager)
