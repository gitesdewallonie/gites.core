# -*- coding: utf-8 -*-
from five import grok
from zope import interface
from gites.core.interfaces import IMapViewletManager
from gites.map.browser.interfaces import IGitesMap
grok.templatedir('templates')
grok.context(interface.Interface)


class MapViewletManager(grok.ViewletManager):
    grok.name('gites.mapviewlet')
    grok.provides(IMapViewletManager)
    grok.layer(IGitesMap)

# register all viewlets in this viewlet manager:
grok.viewletmanager(MapViewletManager)
