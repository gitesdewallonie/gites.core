# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from five import grok
from zope.interface import Interface
from Products.CMFCore.utils import getToolByName

grok.context(Interface)


class FooterView(grok.View):
    """
    Return footer contents
    """
    grok.name('footer_view')
    grok.require('zope2.View')

    def getContent(self, contentId):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        footerFolder = getattr(portal, 'footer', None)
        if footerFolder is None:
            return
        content = footerFolder.restrictedTraverse(contentId, default=None)
        if content is not None:
            translation = content.getTranslation()
            return translation

    def render(self):
        pass
