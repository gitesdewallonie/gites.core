# -*- coding: utf-8 -*-
"""
gites.core
----------

Created by mpeeters
:copyright: (c) 2015 by Affinitic SPRL
:license: GPL, see LICENCE.txt for more details.
"""

from five import grok
from zope.interface import Interface
from plone import api

import urllib

from gites.core import utils


class LinkView(grok.View):
    grok.context(Interface)
    grok.name('l')
    grok.require('zope2.View')

    def render(self):
        portal_url = api.portal.get().absolute_url()
        url = self.request.get('u', portal_url)
        url = urllib.unquote(url)
        md5 = self.request.get('m')
        md5_comparison = utils.calculate_md5(url)
        if md5_comparison != md5:
            url = portal_url
        self.request.RESPONSE.redirect(url)
