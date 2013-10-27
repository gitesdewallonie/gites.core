# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from zope.interface import implements
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from z3c.sqlalchemy import getSAWrapper
from sqlalchemy import and_
from Products.Five import BrowserView

from gites.core.browser.interfaces import ITypeHebView


class TypeHebView(BrowserView):
    """
    Vue sur un type d hebergement
    """
    implements(ITypeHebView)
    __name__ = 'index.html'

    render = ZopeTwoPageTemplateFile("templates/type_heb_view.pt")

    def __init__(self, typeHeb, request):
        self.request = request
        self.context = typeHeb
        self.typeHeb = typeHeb

    def typeHebergementName(self):
        """
        Get the hebergement type title translated
        """
        language = self.request.get('LANGUAGE', 'en')
        return self.typeHeb.getTitle(language)

    def getHebergements(self):
        """
        Return the concerned hebergements for the selected type of hebergement
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        HebergementTable = wrapper.getMapper('hebergement')
        HebergementAppTable = wrapper.getMapper('hebergement_app')
        ProprioTable = wrapper.getMapper('proprio')
        query = session.query(HebergementTable).join('app')
        hebergements = query.filter(HebergementTable.heb_typeheb_fk == self.typeHeb.type_heb_pk)
        hebergements = hebergements.filter(and_(HebergementTable.heb_site_public == '1',
                                                ProprioTable.pro_etat == True))
        hebergements = hebergements.order_by(HebergementAppTable.heb_app_sort_order)
        hebergements = [hebergement.__of__(self.context.hebergement) for hebergement in hebergements]
        return hebergements

    def __call__(self):
        return self.render()
