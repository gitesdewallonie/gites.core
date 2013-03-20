# -*- coding: utf-8 -*-
from Acquisition import aq_inner, aq_parent
from five import grok
from zope import interface
from datetime import datetime
from plone.app.layout.navigation.interfaces import INavigationRoot

grok.templatedir('templates')
grok.context(interface.Interface)


class FooterViewletManager(grok.ViewletManager):
    grok.name('gites.footer')


class VideoFooterViewlet(grok.Viewlet):
    grok.order(10)

    def available(self):
        return self.isMainPage()

    def getUrl(self):
        language = self.request.get('LANGUAGE', 'fr')
        if language == 'fr':
            return 'http://www.youtube.com/embed/mQNk9xSErBg'
        elif language == 'nl':
            return 'http://www.youtube.com/embed/BCJHP0T8g0k'
        else:
            return 'http://www.youtube.com/embed/qZ41Dpgqgds'

    def isMainPage(self):
        obj = aq_inner(self.context)
        if INavigationRoot.providedBy(aq_parent(obj)):
            return True
        else:
            return False


class InfosFooterViewlet(grok.Viewlet):
    grok.order(20)


class BannerFooterViewlet(grok.Viewlet):
    grok.order(30)

    def getYear(self):
        return datetime.now().year


# register all viewlets in this viewlet manager:
grok.viewletmanager(FooterViewletManager)
