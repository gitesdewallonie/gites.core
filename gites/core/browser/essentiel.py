# -*- coding: utf-8 -*-
from five import grok
from zope import interface

grok.templatedir('templates')
grok.context(interface.Interface)


class EssentielViewletManager(grok.ViewletManager):
    grok.name('gites.essentiel')

class EssentielViewlet(grok.Viewlet):
    pass

# register all viewlets in this viewlet manager:
grok.viewletmanager(EssentielViewletManager)
