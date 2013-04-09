# -*- coding: utf-8 -*-
"""
gites.skin

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from zope.interface import implements
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from z3c.sqlalchemy import getSAWrapper
from sqlalchemy import and_
from Products.Five import BrowserView

from gites.core.browser.interfaces import ITypeHebCommuneView


class TypeHebCommuneView(BrowserView):
    """
    Vue sur un type d hebergement et une commune
    """
    implements(ITypeHebCommuneView)
    __name__ = 'index.html'

    render = ZopeTwoPageTemplateFile("templates/type_heb_commune_view.pt")

    def __init__(self, commune, request):
        self.request = request
        self.typeHeb = commune.aq_parent
        self.context = commune
        self.commune = commune

    def typeHebergementName(self):
        """
        Get the hebergement type title translated
        """
        language = self.request.get('LANGUAGE', 'en')
        return self.typeHeb.getTitle(language)

    def communeName(self):
        """
        Get the name of the commune
        """
        return self.commune.com_nom

    def getHebergements(self):
        """
        Return the concerned hebergements in this Town for the selected
        type of hebergement
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        HebergementTable = wrapper.getMapper('hebergement')
        CommuneTable = wrapper.getMapper('commune')
        ProprioTable = wrapper.getMapper('proprio')
        query = session.query(HebergementTable).join('commune').join('proprio')
        hebergements = query.filter(and_(CommuneTable.com_id == self.commune.com_id,
                                         HebergementTable.heb_typeheb_fk == self.typeHeb.type_heb_pk))
        hebergements = hebergements.filter(and_(HebergementTable.heb_site_public == '1',
                                                ProprioTable.pro_etat == True))
        hebergements = hebergements.order_by(HebergementTable.heb_nom)
        hebergements = [hebergement.__of__(self.context.hebergement) for hebergement in hebergements]
        return hebergements

    def __call__(self):
        return self.render()
