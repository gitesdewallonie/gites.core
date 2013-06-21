# -*- coding: utf-8 -*-
from datetime import date
from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, or_, select

from z3c.sqlalchemy import getSAWrapper
from zope.formlib import form
from five.formlib import formbase

import plone.z3cform.z2
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from gites.locales import GitesMessageFactory as _
from gites.core.interfaces import IMapRequest
from gites.core.browser.interfaces import (ISearchHebergement,
                                           IBasicSearchHebergement,
                                           IBasicSearchHebergementTooMuch,
                                           ISearchHebergementTooMuch)


class SearchHebergement(formbase.PageForm):
    """
    A search module to search hebergement
    """
    label = _("Search Hebergement")
    form_reset = False

    form_fields = form.FormFields(ISearchHebergement)
    too_much_form_fields = form.FormFields(ISearchHebergementTooMuch)

    search_results = ViewPageTemplateFile('templates/search_results_hebergement.pt')

    def update(self):
        self.request.locale = plone.z3cform.z2.setup_locale(self.request)
        super(SearchHebergement, self).update()

    def getCommuneForLocalite(self, localite):
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        hebergementTable = wrapper.getMapper('hebergement')
        communeTable = wrapper.getMapper('commune')
        query = session.query(communeTable).join('relatedHebergement')
        query = query.filter(and_(hebergementTable.heb_com_fk == communeTable.com_pk,
                                  hebergementTable.heb_localite == localite))
        commune = query.first()
        return commune

    def translateGroupedType(self, groupedType):
        """
        Translate a grouped type to a list of types
        """
        if groupedType == -2:
            types = ['GR', 'GF', 'MT', 'GC', 'MV', 'GRECR', 'GG']
        elif groupedType == -3:
            types = ['CH', 'MH', 'CHECR']
        return self.translateTypes(types)

    def translateTypes(self, types):
        """
        Translate types to a list of types
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        typeHebTable = wrapper.getMapper('type_heb')
        typeList = session.query(typeHebTable).filter(typeHebTable.type_heb_code.in_(types))
        return [typeHeb.type_heb_pk for typeHeb in typeList]

    def sortSearchResults(self, results, communeLocalite):
        """
        les hébergements de la commune / localité recherchée doivent
        apparaître en premier
        """
        sortedResults = []
        firstResults = []
        nextResults = []
        for heb in results:
            if heb.heb_localite == communeLocalite:
                firstResults.append(heb)
            else:
                nextResults.append(heb)
        sortedResults = firstResults + nextResults
        return sortedResults

    @form.action(_("action_search", u"Rechercher"))
    def action_search(self, action, data):
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        hebergementTable = wrapper.getMapper('hebergement')
        proprioTable = wrapper.getMapper('proprio')
        reservationsTable = wrapper.getMapper('reservation_proprio')
        provincesTable = wrapper.getMapper('province')
        communeTable = wrapper.getMapper('commune')
        episTable = wrapper.getMapper('link_hebergement_epis')
        hebergementType = data.get('hebergementType')
        provinces = data.get('provinces')
        communeLocalite = data.get('communes')
        classification = data.get('classification')
        capacityMin = data.get('capacityMin')
        roomAmount = data.get('roomAmount')
        checkAnimals = data.get('animals')
        checkSmokers = data.get('smokers')
        fromDate = data.get('fromDate')
        toDate = data.get('toDate')
        seeResults = 'form.seeResults' in self.request.form

        translation_service = getToolByName(self.context,
                                            'translation_service')
        utranslate = translation_service.utranslate
        lang = self.request.get('LANGUAGE', 'en')

        query = session.query(hebergementTable).join('province').join('proprio')
        query = query.filter(hebergementTable.heb_site_public == '1')
        query = query.filter(proprioTable.pro_etat == True)

        if communeLocalite and str(communeLocalite) != '-1':
            relatedCommune = self.getCommuneForLocalite(communeLocalite)
            if relatedCommune:
                query = query.filter(and_(hebergementTable.heb_com_fk == communeTable.com_pk,
                                          or_(communeTable.com_nom == communeLocalite,
                                              communeTable.com_nom == relatedCommune.com_nom)))
            else:
                query = query.filter(and_(hebergementTable.heb_com_fk == communeTable.com_pk,
                                          communeTable.com_nom == communeLocalite))
        elif provinces and str(provinces) != '-1':
            # on prend en compte la province que si aucune commune n'est
            # renseignée
            query = query.filter(provincesTable.prov_pk == provinces)
        if hebergementType and str(hebergementType) != '-1':
            if hebergementType in [-2, -3]:
                groupedHebergementTypes = self.translateGroupedType(hebergementType)
                query = query.filter(hebergementTable.heb_typeheb_fk.in_(groupedHebergementTypes))
            else:
                query = query.filter(hebergementTable.heb_typeheb_fk == hebergementType)
        if classification and str(classification) != '-1':
            query = query.filter(and_(episTable.heb_nombre_epis == classification,
                                      hebergementTable.heb_pk == episTable.heb_pk))
        if checkAnimals:
            query = query.filter(hebergementTable.heb_animal == 'oui')
        if checkSmokers:
            query = query.filter(hebergementTable.heb_fumeur == 'oui')
        if roomAmount:
            query = query.filter(hebergementTable.heb_cgt_nbre_chmbre >= roomAmount)
        if capacityMin:
            if capacityMin < 16:
                capacityMax = capacityMin + 4
                query = query.filter(or_(hebergementTable.heb_cgt_cap_min.between(capacityMin, capacityMax),
                                         hebergementTable.heb_cgt_cap_max.between(capacityMin, capacityMax)))
            else:
                capacityMax = capacityMin
                capacityMin = 16
                query = query.filter(and_(hebergementTable.heb_cgt_cap_min >= capacityMin,
                                          hebergementTable.heb_cgt_cap_max >= capacityMax))

        if fromDate or toDate:
            query = query.filter(hebergementTable.heb_calendrier_proprio != 'non actif')
            # on ne considère que les hébergements pour lequel le calendrier
            # est utilisé
            beginDate = fromDate or (toDate + relativedelta(days=-1))
            endDate = toDate or (fromDate + relativedelta(days=+1))
            today = date.today()
            # il ne peut pas y avoir d'enregistrement dans la table de
            # réservations entre les dates de début et de fin (vu que seules
            # les indisponibilités sont dans la table)

            # il y a un décalage dans le calcul des jours / nuits :
            # 1 nuit indiquée comme louée = 2 jours demandés
            # --> >= beginDate et < endDate
            if beginDate < today or endDate < today:
                message = utranslate('gites',
                                     "La recherche n'a pas renvoy&eacute; de r&eacute;sultats.",
                                     target_language=lang,
                                     context=self.context)
                self.errors += (message, )
                self.status = " "
                return self.template()

            busyHeb = select([reservationsTable.heb_fk],
                             and_(reservationsTable.res_date >= beginDate,
                                  reservationsTable.res_date < endDate)).distinct().execute().fetchall()
            busyHebPks = [heb.heb_fk for heb in busyHeb]
            query = query.filter(~hebergementTable.heb_pk.in_(busyHebPks))

        query = query.order_by(hebergementTable.heb_nom)
        results = query.all()
        results = self.sortSearchResults(results, communeLocalite)
        self.selectedHebergements = [hebergement.__of__(self.context.hebergement) for hebergement in results]

        nbResults = len(self.selectedHebergements)
        if nbResults > 50 and not seeResults:    # il faut affiner la recherche
            self.form_fields = self.too_much_form_fields
            form.FormBase.resetForm(self)
            self.widgets['roomAmount'].setRenderedValue(roomAmount)
            self.widgets['capacityMin'].setRenderedValue(capacityMin)
            self.widgets['animals'].setRenderedValue(checkAnimals)
            self.widgets['smokers'].setRenderedValue(checkSmokers)
            self.widgets['hebergementType'].setRenderedValue(hebergementType)
            self.widgets['provinces'].setRenderedValue(provinces)
            self.widgets['communes'].setRenderedValue(communeLocalite)
            self.widgets['classification'].setRenderedValue(classification)
            self.widgets['fromDate'].setRenderedValue(fromDate)
            self.widgets['toDate'].setRenderedValue(toDate)

            message = utranslate('gites',
                                 "La recherche a renvoy&eacute; ${nbr} r&eacute;sultats. <br /> Il serait utile de l'affiner.",
                                 {'nbr': nbResults},
                                 target_language=lang,
                                 context=self.context)
            self.errors += (message, )
            self.status = " "
            return self.template()

        else:   # on montre tous les resultats, independamment du nombre
            if nbResults == 0:
                message = utranslate('gites',
                                     "La recherche n'a pas renvoy&eacute; de r&eacute;sultats.",
                                     target_language=lang,
                                     context=self.context)
                self.errors += (message, )
                self.status = " "
                return self.template()
            else:
                return self.search_results()


class BasicSearchHebergement(SearchHebergement):
    """
    A search module to search hebergement
    """
    label = _("Search Hebergement")
    form_reset = False

    form_fields = form.FormFields(IBasicSearchHebergement)
    too_much_form_fields = form.FormFields(IBasicSearchHebergementTooMuch)

    template = ViewPageTemplateFile('templates/search_results_hebergement.pt')

    def update(self):
        self.request.locale = plone.z3cform.z2.setup_locale(self.request)
        super(BasicSearchHebergement, self).update()


##############
## z3c.form ##
##############

import zope.interface
from z3c.form import form, field
from five import grok
from plone.z3cform import layout

from gites.core.browser import interfaces
from collective.z3cform.datepicker.widget import DatePickerFieldWidget
from z3c.form import button
from Acquisition import aq_inner


class BasicForm(form.Form):
    fields = field.Fields(interfaces.ISearchHosting).select(
        'hebergementType',
        'capacityMin',
        'fromDate',
        'toDate')

    ignoreContext = True
    fields['fromDate'].widgetFactory = DatePickerFieldWidget
    fields['toDate'].widgetFactory = DatePickerFieldWidget

    template = ViewPageTemplateFile('templates/search_base_form.pt')

    def selected_gite(self):
        """
        """
        heb_type = self.request.form.get('form.widgets.hebergementType')
        if not heb_type or 'gite-meuble' in heb_type:
            return 'checked'

    def selected_chambre(self):
        """
        """
        heb_type = self.request.form.get('form.widgets.hebergementType')
        if not heb_type or 'chambre-hote' in heb_type:
            return 'checked'

class SearchHostingForm(form.Form):
    fields = field.Fields(interfaces.ISearchHosting).select(
        'hebergementType',
        'classification',
        'capacityMin',
        'roomAmount',
        'animals',
        'smokers',
        'fromDateAvancee',
        'toDateAvancee',
        'nearTo')

    label = _("Search Hebergement")
    ignoreContext = True
    fields['fromDateAvancee'].widgetFactory = DatePickerFieldWidget
    fields['toDateAvancee'].widgetFactory = DatePickerFieldWidget

    template = ViewPageTemplateFile('templates/search_host_form.pt')

    def selected_gite(self):
        """
        """
        heb_type = self.request.form.get('form.widgets.hebergementType')
        if not heb_type or 'gite-meuble' in heb_type:
            return 'checked'

    def selected_chambre(self):
        """
        """
        heb_type = self.request.form.get('form.widgets.hebergementType')
        if not heb_type or 'chambre-hote' in heb_type:
            return 'checked'

class SearchHosting(layout.FormWrapper, grok.View):
    grok.context(zope.interface.Interface)
    grok.name('search_hosting.html')
    grok.require('zope2.Public')

    form = SearchHostingForm
