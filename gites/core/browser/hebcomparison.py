# encoding: utf-8
"""
gites.core

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

import sqlalchemy as sa

import zope.interface
from five import grok

from gites.db import content as mappers, session
from gites.locales import GitesMessageFactory as _

from gites.core import interfaces
from gites.core.table import hebcomparison


class HebComparisonView(grok.View):
    grok.context(zope.interface.Interface)
    grok.name(u'hebergement-comparison')
    grok.require('zope2.View')
    grok.template('hebcomparison')

    def update(self):
        query = session().query(mappers.Hebergement.heb_pk)
        query = query.join('proprio')
        query = query.filter(sa.and_(
            mappers.Hebergement.heb_pk.in_(self.request.get('heb_pk')),
            mappers.Hebergement.heb_site_public == '1',
            mappers.Proprio.pro_etat == True))
        self.heb_pks = set([heb.heb_pk for heb in query.all()])

    def get_table(self):
        """ Returns the render of the table """
        table = hebcomparison.HebComparisonTable(self.context,
                                                 self.request,
                                                 self.heb_pks)
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
        for heb_pk in self.hebs_with_active_calendar:
            content = "%s%s" % (content, calendar_js % {
                'heb_pk': heb_pk,
                'language': self.request.get('LANGUAGE', 'en')})
        return content

    @property
    def hebs_with_active_calendar(self):
        """ Returns the heb_pk for the heb who have an active calendar """
        query = session().query(mappers.Hebergement.heb_pk)
        query = query.filter(sa.and_(
            mappers.Hebergement.heb_pk.in_(self.heb_pks),
            mappers.Hebergement.heb_calendrier_proprio == 'actif'))
        return [heb.heb_pk for heb in query.all()]

    def validate(self):
        if len(self.heb_pks) < 2:
            self.error = _(u'compare_less_than_2')
            return False
        if len(self.heb_pks) > 4:
            self.error = _(u'compare_more_than_4')
            return False
        if self._as_heb_mix_type is True:
            self.error = _(u'compare_mix_type')
            return False
        return True

    @property
    def _as_heb_mix_type(self):
        """ Verifies if there's multiple hosting type """
        query = session().query(mappers.Hebergement.heb_pk,
                                mappers.TypeHebergement.type_heb_code)
        query = query.join('type')
        query = query.filter(
            mappers.Hebergement.heb_pk.in_(self.heb_pks))
        types = []
        for heb in query.all():
            types.append(heb.type_heb_code in ('CH', 'MH', 'CHECR'))
        return len(set(types)) > 1
