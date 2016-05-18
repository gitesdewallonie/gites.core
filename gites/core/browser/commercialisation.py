# -*- coding: utf-8 -*-
"""
gites.skin

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

"""
from Products.Five import BrowserView
from zope.interface import implements
from gites.core.browser.interfaces import ICommercialisationView


class CommercialisationView(BrowserView):
    """
    View for the commercialisation of an hebergement
    """
    implements(ICommercialisationView)

    def getUrlCommercialisation(self, hebCommercialisationId):
        """
        Get the url for the Alliance belholidays
        url fournie par belholidays :
        près le wos mettre le heb_commercialisation _id
        http://reservation.belholidays.com/z11593_nl-.aspx?_wos=
        """
        language = self.request.get('LANGUAGE', 'en')
        import pdb; pdb.set_trace()
        url = ''
        if language == "nl":
            url = "http://reservation.belholidays.com/z11593_nl-.aspx?_wos=%s" % (hebCommercialisationId)
        if language in ("en", "it", "de"):
            url = "http://reservation.belholidays.com/z11593_uk-.aspx?_wos=%s" % (hebCommercialisationId)
        if language == ("fr"):
            url = "http://reservation.belholidays.com/z11593_fr-.aspx?_wos=%s" % (hebCommercialisationId)

        return url
