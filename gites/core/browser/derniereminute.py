# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from five import grok
from gites.core.content.interfaces import IDerniereMinute
from zope.interface import Interface
from bs4 import BeautifulSoup

grok.context(Interface)


class DerniereMinuteView(grok.View):
    """
    View on Idee Sejour
    """
    grok.context(IDerniereMinute)
    grok.name('dernieres_minutes_view')
    grok.require('zope2.View')

    def getNiceEventStartDate(self):
        """
        """
        startDate = self.context.getEventStartDate()
        return startDate.strftime("%d-%m")

    def getNiceEventEndDate(self):
        """
        """
        endDate = self.context.getEventEndDate()
        return endDate.strftime("%d-%m")

    def getText(self):
        """
        """
        texte = self.context.getText()
        b = BeautifulSoup(texte)
        paragraph = b.find('p')
        if paragraph:
            return paragraph.renderContents()
        else:
            return texte

    def getTypeHebergement(self):
        language = self.request.get('LANGUAGE', 'en')
        return self.context.getHebergement().type.getTitle(language)

    def render(self):
        pass
