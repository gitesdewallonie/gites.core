# -*- coding: utf-8 -*-
from five import grok
from zope import interface

grok.templatedir('templates')
grok.context(interface.Interface)


class HeaderViewletManager(grok.ViewletManager):
    grok.name('gites.header')


class TopHeaderViewlet(grok.Viewlet):
    grok.order(10)


class MainHeaderViewlet(grok.Viewlet):
    grok.order(20)

    def getTranslatedObjectUrl(self, path):
        """
        """
        obj = self.context.restrictedTraverse(path)
        translatedObject = obj.getTranslation()
        if translatedObject:
            url = translatedObject.absolute_url()
        else:
            url = obj.absolute_url()
        return url

# register all viewlets in this viewlet manager:
grok.viewletmanager(HeaderViewletManager)
