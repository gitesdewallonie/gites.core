# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from Products.Five.site import localsite
from zope.event import notify
from ExtensionClass import Base
from zope.app.publication.zopepublication import BeforeTraverseEvent


class LocalSiteHook(Base):

    def __call__(self, container, request):
        notify(BeforeTraverseEvent(container, request))

localsite.LocalSiteHook = LocalSiteHook
