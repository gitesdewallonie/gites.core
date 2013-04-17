# -*- coding: utf-8 -*-
"""
gites.skin

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from Products.Five.browser import BrowserView


class Translate(BrowserView):
    """
    Translate object
    """

    def getTranslatedObjectUrl(self, path):
        """
        """
        obj = self.context.restrictedTraverse(path, default=None)
        if obj is None:
            return ''
        translatedObject = obj.getTranslation()
        if translatedObject:
            url = translatedObject.absolute_url()
        else:
            url = obj.absolute_url()
        return url
