# -*- coding: utf-8 -*-

from urlparse import urljoin
from Products.Five import BrowserView
from zope.interface import implements
from sqlalchemy import and_
from z3c.sqlalchemy import getSAWrapper
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from affinitic.db.cache import FromCache

from gites.core.browser.interfaces import IHebergementView


class HebergementExternCalendarView(BrowserView):
    """
    View for extern calendars
    """
    implements(IHebergementView)
    template = ViewPageTemplateFile("templates/externcalendar.pt")

    def __init__(self, context, request):
        hebPk = request.get('pk')
        hebergement = self.getHebergementByPk(hebPk)
        self.hebergement = hebergement
        super(BrowserView, self).__init__(context, request)

    def getHebergementByPk(self, heb_pk):
        """
        Get the url of the hebergement by Pk
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        HebTable = wrapper.getMapper('hebergement')
        try:
            int(heb_pk)
        except ValueError:
            return None
        hebergement = session.query(HebTable).options(FromCache('gdw')).get(heb_pk)
        if (hebergement and
                int(hebergement.heb_site_public) == 1 and
                hebergement.proprio.pro_etat):
            return hebergement
        else:
            return None

    def showCalendar(self):
        """
        Is the calendar activated for showing on external sites ?
        (if the calendar has been blocked due to inactivity, it will not
        appear because heb_calendrier_proprio will be 'bloque' by cron)
        """
        if self.hebergement is None:
            return False
        return (self.hebergement.heb_calendrier_proprio == 'actif')

    def getCustomStylesheet(self):
        """
        Returns referer stylesheet URL where proprio can customize calendar
        CSS
        """
        referer = self.request.get('HTTP_REFERER', None)
        customCssUrl = urljoin(referer, 'calendar-custom.css')
        return customCssUrl

    def calendarJS(self):
        """
        Calendar javascript
        """
        return """
        //<![CDATA[
            new GiteTimeframe('calendars', {
                              startField: 'start',
                              endField: 'end',
                              resetButton: 'reset',
                              weekOffset: 1,
                              hebPk: %s,
                              months:1,
                              language: '%s',
                              earliest: new Date()});
        //]]>

        """ % (self.hebergement.heb_pk, 'fr')


class HebergementExternMonthlyCalendarView(BrowserView):
    """
    View for extern monthly calendars
    """
    implements(IHebergementView)
    template = ViewPageTemplateFile("templates/externmonthlycalendar.pt")

    def __init__(self, context, request):
        proPk = request.get('pk')
        hebergements = self.getHebergementsForProprio(proPk)
        self.hebergements = hebergements
        super(BrowserView, self).__init__(context, request)

    def cleanupUnicodeForJS(self, text):
        text = text.replace("[u'", "['").replace(", u'", ", '")
        text = text.replace('[u"', '["').replace(', u"', ', "')
        return text

    def getHebergementsForProprio(self, proprioPk):
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        Proprio = wrapper.getMapper('proprio')
        query = session.query(Proprio)
        query = query.filter(and_(Proprio.pro_pk == int(proprioPk),
                                  Proprio.pro_etat == True))
        proprietaire = query.one()
        hebs = proprietaire.hebergements
        publicHebs = []
        for heb in hebs:
            if heb.heb_site_public == '1' and \
               heb.heb_calendrier_proprio == 'actif':
                publicHebs.append(heb)
        publicHebs.sort(key=lambda x: x.heb_pk)
        return publicHebs

    def calendarJS(self):
        """
        Calendar javascript
        """
        hebPks = [int(heb.heb_pk) for heb in self.hebergements]
        hebNames = [heb.heb_nom for heb in self.hebergements]
        return self.cleanupUnicodeForJS("""
        //<![CDATA[
            new GiteMultiTimeframe('calendars', {
                                   startField: 'start',
                                   endField: 'end',
                                   resetButton: 'reset',
                                   months: 1,
                                   weekOffset: 1,
                                   hebsPks: %s,
                                   hebsNames: %s,
                                   language: '%s',
                                   earliest: new Date()});
        //]]>

        """ % (hebPks, hebNames, 'fr'))
