# -*- coding: utf-8 -*-
from five import grok
from zope import interface, component
from gites.core.interfaces import IHebergementsFetcher
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
import random

grok.templatedir('templates')
grok.context(interface.Interface)


class HeaderViewletManager(grok.ViewletManager):
    grok.name('gites.header')

class TopHeaderViewlet(grok.Viewlet):
    grok.order(10)
    grok.viewletmanager(HeaderViewletManager)

class MainHeaderViewlet(grok.Viewlet):
    grok.order(20)
    grok.viewletmanager(HeaderViewletManager)

# register all viewlets in this viewlet manager:
grok.viewletmanager(HeaderViewletManager)
