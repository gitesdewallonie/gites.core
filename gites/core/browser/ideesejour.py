# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from five import grok
from gites.core.content.interfaces import IIdeeSejour
from zope.interface import Interface
from z3c.sqlalchemy import getSAWrapper

grok.context(Interface)
grok.templatedir('templates')


class IdeeSejour(grok.View):
    """
    View on Idee Sejour
    """
    grok.context(IIdeeSejour)
    grok.name('idee_sejour_view')
    grok.require('zope2.View')

    def getHebergements(self):
        """
        return the list of hebergement available in the current idee sejour
        """
        wrapper = getSAWrapper('gites_wallons')
        Hebergements = wrapper.getMapper('hebergement')
        session = wrapper.session
        hebList = [int(i) for i in self.context.getHebergements()]
        hebergements = session.query(Hebergements).filter(Hebergements.heb_pk.in_(hebList))
        hebergements = list(set(hebergements))
        hebergements.sort(lambda x, y: cmp(x.heb_nom, y.heb_nom))
        hebergements = [hebergement.__of__(self.context.hebergement) for hebergement in hebergements]
        return hebergements