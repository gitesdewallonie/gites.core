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

# register all viewlets in this viewlet manager:
grok.viewletmanager(HeaderViewletManager)
