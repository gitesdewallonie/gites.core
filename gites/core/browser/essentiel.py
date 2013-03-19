# -*- coding: utf-8 -*-
from Acquisition import aq_inner, aq_parent
from five import grok
from zope import interface
from plone.app.layout.navigation.interfaces import INavigationRoot

grok.templatedir('templates')
grok.context(interface.Interface)


class EssentielViewletManager(grok.ViewletManager):
    grok.name('gites.essentiel')

class EssentielViewlet(grok.Viewlet):

    def isMainPage(self):
        obj = aq_inner(self.context)
        if INavigationRoot.providedBy(aq_parent(obj)):
            return True
        else:
            return False

# register all viewlets in this viewlet manager:
grok.viewletmanager(EssentielViewletManager)
