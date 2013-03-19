# -*- coding: utf-8 -*-
from five import grok
from zope import interface, component
from gites.core.interfaces import IHebergementsFetcher
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
import random

grok.templatedir('templates')
grok.context(interface.Interface)


class FooterViewletManager(grok.ViewletManager):
    grok.name('gites.footer')

class VideoFooterViewlet(grok.Viewlet):
    def getUrl(self):
        langage = u'fr'
        if langage == u'fr':
            return 'http://www.youtube.com/embed/mQNk9xSErBg'
        elif langage == u'nl':
            return 'http://www.youtube.com/embed/BCJHP0T8g0k'
        else:
            return 'http://www.youtube.com/embed/qZ41Dpgqgds'

    grok.order(10)
    grok.viewletmanager(FooterViewletManager)

class InfosFooterViewlet(grok.Viewlet):
    grok.order(20)
    grok.viewletmanager(FooterViewletManager)

class BannerFooterViewlet(grok.Viewlet):
    grok.order(30)
    grok.viewletmanager(FooterViewletManager)

# register all viewlets in this viewlet manager:
grok.viewletmanager(FooterViewletManager)
