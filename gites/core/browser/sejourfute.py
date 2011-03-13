# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from five import grok
from gites.core.content.interfaces import ISejourFute
from zope.interface import Interface
from z3c.sqlalchemy import getSAWrapper

grok.context(Interface)
grok.templatedir('templates')


class SejourFute(grok.View):
    """
    View on Idee Sejour
    """
    grok.context(ISejourFute)
    grok.name('sejour_fute_view')
    grok.require('zope2.View')

    def getHebergements(self):
        """
        Return the concerned hebergements by this Sejour fute
        = hebergements linked to the Maison du tourism +
          select hebergements
        """
        wrapper = getSAWrapper('gites_wallons')
        Hebergements = wrapper.getMapper('hebergement')
        Proprio = wrapper.getMapper('proprio')
        session = wrapper.session

        relatedHebs = self.context.getHebPks()
        query = session.query(Hebergements).join('proprio')
        query = query.filter(Hebergements.heb_pk.in_(relatedHebs))
        query = query.filter(Hebergements.heb_site_public == '1')
        query = query.filter(Proprio.pro_etat == True)
        query = query.order_by(Hebergements.heb_nom)
        hebergements = query.all()
        hebergements = [hebergement.__of__(self.context.hebergement) for hebergement in hebergements]
        return hebergements
