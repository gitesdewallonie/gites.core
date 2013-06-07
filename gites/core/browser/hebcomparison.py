# encoding: utf-8
"""
gites.core

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

import zope.interface
from five import grok

from gites.core import interfaces
from gites.core.table import hebcomparison
from gites.db import content as mappers, session


class HebComparisonView(grok.View):
    grok.context(zope.interface.Interface)
    grok.name(u'hebergement-comparison')
    grok.require('zope2.View')
    grok.template('hebcomparison')

    def get_table(self):
        """ Returns the render of the table """
        table = hebcomparison.HebComparisonTable(self.context,
                                                 self.request)
        if len(self.request.get('heb_pk')) == 3:
            zope.interface.alsoProvides(
                table, interfaces.IHebergementComparisonThree)
        elif len(self.request.get('heb_pk')) == 4:
            zope.interface.alsoProvides(
                table, interfaces.IHebergementComparisonFour)
        table.update()
        return table.render()

    def calendarJS(self):
        """
        Calendar javascript
        """
        calendar_js = """
calsetup%(heb_pk)s = function() {
    jQuery.noConflict();
    new GiteTimeframe('calendars%(heb_pk)s', {
                      startField: 'start',
                      endField: 'end',
                      resetButton: 'reset',
                      weekOffset: 1,
                      hebPk: %(heb_pk)s,
                      months:1,
                      language: '%(language)s',
                      earliest: new Date()});
    var elements = $('calendars%(heb_pk)s_menu').childElements();
    var customClick = function() {
        var element = $(this);
        jQuery('.' + $(this).classList[1]).each(function() {
            if ($(this) != element) {
                $(this).fire('custom:click');
            };
        });
    };
    for (idx in elements){
        if (isNaN(idx) === true) {
            break;
        }
        var element = elements[idx].firstDescendant();
        element.observe('click', customClick.bind(element));
    }
}
registerPloneFunction(calsetup%(heb_pk)s);"""
        content = ""
        for heb_pk in self.request.get('heb_pk'):
            if self.is_active_calendar(heb_pk) is False:
                continue
            content = "%s%s" % (content, calendar_js % {
                'heb_pk': heb_pk,
                'language': self.request.get('LANGUAGE', 'en')})
        return content

    def is_active_calendar(self, heb_pk):
        query = session().query(mappers.Hebergement.heb_calendrier_proprio)
        query = query.filter(mappers.Hebergement.heb_pk == heb_pk)
        result = query.first()
        return getattr(result, 'heb_calendrier_proprio', None) == 'actif'
