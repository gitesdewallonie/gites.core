# -*- coding: utf-8 -*-
"""
gites.skin

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from affinitic.db.cache import FromCache
from micawber.exceptions import InvalidResponseException
from micawber.exceptions import ProviderException
from micawber.exceptions import ProviderNotFoundException
from plone import api
from plone.memoize import instance, forever
from plone.memoize.instance import memoize
from z3c.sqlalchemy import getSAWrapper
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import queryMultiAdapter
from zope.i18n import translate
from zope.interface import alsoProvides, implements
from zope.traversing.browser.interfaces import IAbsoluteURL
import micawber
import sqlalchemy as sa
import urllib
import zope.interface

from gites.db.content import Hebergement, HebergementApp, TypeHebergement, LinkHebergementEpis, Proprio, Commune
from gites.db.content.hebergement.metadata import Metadata
from gites.locales import GitesMessageFactory as _
from gites.map.browser.interfaces import IMappableView

from gites.core import interfaces
from gites.core import utils
from gites.core.browser.interfaces import (IHebergementView,
                                           IHebergementIconsView)
from gites.core.browser.tarif import TarifTableMixin
from gites.core.interfaces import IMapRequest
from gites.core.table import tarif


@forever.memoize
def getIframeForVideo(videoUrl):
    providers = micawber.bootstrap_basic()
    try:
        embed = providers.request(videoUrl, maxwidth=580, maxheight=377)
    except (InvalidResponseException,
            ProviderException,
            ProviderNotFoundException):
        return None
    return embed['html']


class HebergementView(BrowserView, TarifTableMixin):
    """
    View for the full description of an hebergement
    """
    implements(IHebergementView, IMappableView)
    template = ViewPageTemplateFile("templates/hebergement.pt")

    def __init__(self, context, request):
        super(HebergementView, self).__init__(context, request)
        super(BrowserView, self).__init__(context, request)
        alsoProvides(self.request, IMapRequest)

    def calendarJS(self):
        """
        Calendar javascript
        """
        return """
        //<![CDATA[
            calsetup = function() {
                jQuery.noConflict();
                new GiteTimeframe('calendars', {
                                startField: 'start',
                                endField: 'end',
                                resetButton: 'reset',
                                weekOffset: 1,
                                hebPk: %s,
                                months:1,
                                language: '%s',
                                earliest: new Date()});}
            registerPloneFunction(calsetup);
        //]]>

        """ % (self.context.heb_pk,
               self.request.get('LANGUAGE', 'en'))

    def dispoCalendarJS(self):
        """
        Calendar javascript
        """
        return """
        //<![CDATA[
            calsetup = function() {
                jQuery.noConflict();
                new GiteTimeframe('dispocalendars', {
                                startField: 'dispostart',
                                endField: 'dispoend',
                                resetButton: 'disporeset',
                                weekOffset: 1,
                                hebPk: %s,
                                months:6,
                                language: '%s',
                                earliest: new Date()});}
            registerPloneFunction(calsetup);
        //]]>

        """ % (self.context.heb_pk,
               self.request.get('LANGUAGE', 'en'))

    def showCalendar(self):
        """
        Is the calendar activated for showing in description ?
        (if the calendar has been blocked due to inactivity, it will not
        appear because heb_calendrier_proprio will be 'bloque' by cron)
        """
        return (self.context.heb_calendrier_proprio == 'actif')

    def redirectInactive(self):
        """
        Redirect if gites / proprio is not active
        """
        if (self.context.heb_site_public == '0' or
                self.context.proprio.pro_etat == False):
            url = getToolByName(self.context, 'portal_url')()
            return self.request.response.redirect(url)

    def getTypeHebergement(self):
        """
        Get the hebergement type title translated
        """
        language = self.request.get('LANGUAGE', 'en')
        return self.context.type.getTitle(language)

    def getHebergementSituation(self):
        """
        Get the hebergement type title translated
        """
        language = self.request.get('LANGUAGE', 'en')
        return self.context.getSituation(language)

    @instance.memoize
    def getHebergementDescription(self):
        """
        Get the hebergement type title translated
        """
        language = self.request.get('LANGUAGE', 'en')
        return self.context.getDescription(language)

    @instance.memoize
    def getHebergementCharge(self):
        """
        Get the hebergement type title translated
        """
        language = self.request.get('LANGUAGE', 'en')
        return self.context.charge.getTitle(language)

    def getHebergementDistribution(self):
        """
        Get the hebergement type title translated
        """
        language = self.request.get('LANGUAGE', 'en')
        return self.context.getDistribution(language)

    def getHebergementSeminaireVert(self):
        """
        Get the hebergement seminaire vert information translated
        """
        language = self.request.get('LANGUAGE', 'en')
        return self.context.getSeminaireVert(language)

    def getTypeHebInCommuneURL(self):
        """
        Get the commune and type hebergement URL
        """
        hebURL = queryMultiAdapter((self.context, self.request), name="url")
        urlList = str(hebURL).split('/')
        urlList.pop()
        return '/'.join(urlList)

    def getHebMetadatasByType(self, metadataType):
        """
        Return all metadata objects corresponding on metadataType
        cf: table metadata column metadata_type_id
        """
        heb = self.context
        dics = []
        language = self.request.get('LANGUAGE')
        for md in heb.activeMetadatas:
            if md.metadata_type_id == metadataType:
                dics.append({"id": md.met_id,
                             "title": md.getTitre(language)})
        return dics

    def getAnimal(self):
        list = self.getHebMetadatasByType('autorisations')
        for item in list:
            if item['id'] == 'heb_animal':
                return {'id': 'heb_animal',
                        'title': item['title']}
        return {'id': 'heb_animal_off',
                'title': _(u'animaux_interdits')}

    def getFumeur(self):
        list = self.getHebMetadatasByType('autorisations')
        for item in list:
            if item['id'] == 'heb_fumeur':
                return {'id': 'heb_fumeur',
                        'title': item['title']}
        return {'id': 'heb_fumeur_off',
                'title': _(u'hebergement_non_fumeur')}

    def getTablesHotes(self):
        tablesHotes = self.getHebMetadatasByType('tablehote')
        return tablesHotes

    def render(self):
        return self.template()

    def getVignettesUrl(self):
        """
        Get the vignette of an hebergement
        """
        utool = getToolByName(self.context, 'portal_url')
        portal = utool.getPortalObject()
        photoStorage = getattr(portal, 'photos_heb')
        vignettes = []
        codeGDW = self.context.heb_code_gdw
        listeImage = photoStorage.fileIds()
        for i in range(40):
            if i < 10:
                photo = "%s0%s.jpg" % (codeGDW, i)
            else:
                photo = "%s%s.jpg" % (codeGDW, i)
            if photo in listeImage:
                vignettes.append(photo)
        return vignettes

    def getPhotoContact(self):
        utool = getToolByName(self.context, 'portal_url')
        portal = utool.getPortalObject()
        photoStorage = getattr(portal, 'photos_proprio')
        proPk = self.context.heb_pro_fk
        photoName = "%s.jpg" % proPk
        if photoName in photoStorage.fileIds():
            return photoName
        else:
            return None

    def getIframeForVideo(self, video):
        """
        Get embedly generated iframe for video
        """
        if not video:
            return
        videoUrl = video.heb_vid_url
        return getIframeForVideo(videoUrl)

    def getGroupementByPk(self, hebPk):
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        query = session.query(Hebergement.heb_nom.label('heb_nom'),
                              Hebergement.heb_cgt_nbre_chmbre.label('heb_cgt_nbre_chmbre'),
                              Hebergement.heb_cgt_cap_min.label('heb_cgt_cap_min'),
                              Hebergement.heb_cgt_cap_max.label('heb_cgt_cap_max'),
                              TypeHebergement.type_heb_id.label('heb_type'),
                              TypeHebergement.type_heb_type.label('heb_type_type'),
                              TypeHebergement.type_heb_code.label('heb_type_code'),
                              Hebergement.heb_code_gdw.label('heb_code_gdw'),
                              Hebergement.heb_pk.label('heb_pk'),
                              LinkHebergementEpis.heb_nombre_epis.label('heb_nombre_epis'),
                              Hebergement.heb_localite.label('heb_localite'),
                              Hebergement.heb_gps_long.label('heb_gps_long'),
                              Hebergement.heb_gps_lat.label('heb_gps_lat'),
                              Hebergement.heb_groupement_pk.label('heb_groupement_pk'),
                              HebergementApp.heb_app_groupement_line_length.label('heb_app_groupement_line_length'),
                              HebergementApp.heb_app_groupement_angle_start.label('heb_app_groupement_angle_start')
                              )
        query = query.join('proprio').outerjoin('epis').join('type').join('app')
        query = query.options(FromCache('gdw'))
        query = query.filter(Hebergement.heb_groupement_pk == hebPk)
        query = query.filter(sa.and_(Hebergement.heb_site_public == '1',
                                     Proprio.pro_etat == True))
        groupement = query.all()
        return groupement

    def getCapaciteTotalGroupementByPk(self, hebPk):
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        query = session.query(Hebergement.heb_nom.label('heb_nom'),
                              Hebergement.heb_cgt_nbre_chmbre.label('heb_cgt_nbre_chmbre'),
                              Hebergement.heb_cgt_cap_min.label('heb_cgt_cap_min'),
                              Hebergement.heb_cgt_cap_max.label('heb_cgt_cap_max'),
                              TypeHebergement.type_heb_id.label('heb_type'),
                              TypeHebergement.type_heb_type.label('heb_type_type'),
                              TypeHebergement.type_heb_code.label('heb_type_code'),
                              Hebergement.heb_code_gdw.label('heb_code_gdw'),
                              Hebergement.heb_pk.label('heb_pk'),
                              LinkHebergementEpis.heb_nombre_epis.label('heb_nombre_epis'),
                              Hebergement.heb_localite.label('heb_localite'),
                              Hebergement.heb_gps_long.label('heb_gps_long'),
                              Hebergement.heb_gps_lat.label('heb_gps_lat'),
                              Hebergement.heb_groupement_pk.label('heb_groupement_pk'),
                              HebergementApp.heb_app_groupement_line_length.label('heb_app_groupement_line_length'),
                              HebergementApp.heb_app_groupement_angle_start.label('heb_app_groupement_angle_start')
                              )
        query = query.join('proprio').outerjoin('epis').join('type').join('app')
        query = query.options(FromCache('gdw'))
        query = query.filter(Hebergement.heb_groupement_pk == hebPk)
        query = query.filter(sa.and_(Hebergement.heb_site_public == '1',
                                     Proprio.pro_etat == True))
        groupement = query.all()
        nbreChambre = 0
        nbrePersonneMin = 0
        nbrePersonneMax = 0
        for heb in groupement:
            nbreChambre = nbreChambre + heb.heb_cgt_nbre_chmbre
            nbrePersonneMin = nbrePersonneMin + heb.heb_cgt_cap_min
            nbrePersonneMax = nbrePersonneMax + heb.heb_cgt_cap_max
        return (nbreChambre, nbrePersonneMin, nbrePersonneMax)

    def getGroupementByPkJson(self):
        import json
        pk = self.request.form['pk']
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        query = session.query(Hebergement.heb_nom.label('heb_nom'),
                              Hebergement.heb_cgt_nbre_chmbre.label('heb_cgt_nbre_chmbre'),
                              Hebergement.heb_cgt_cap_min.label('heb_cgt_cap_min'),
                              Hebergement.heb_cgt_cap_max.label('heb_cgt_cap_max'),
                              TypeHebergement.type_heb_id.label('heb_type'),
                              TypeHebergement.type_heb_type.label('heb_type_type'),
                              TypeHebergement.type_heb_code.label('heb_type_code'),
                              Hebergement.heb_code_gdw.label('heb_code_gdw'),
                              Hebergement.heb_pk.label('heb_pk'),
                              LinkHebergementEpis.heb_nombre_epis.label('heb_nombre_epis'),
                              Hebergement.heb_localite.label('heb_localite'),
                              Hebergement.heb_gps_long.label('heb_gps_long'),
                              Hebergement.heb_gps_lat.label('heb_gps_lat'),
                              Hebergement.heb_groupement_pk.label('heb_groupement_pk'),
                              HebergementApp.heb_app_groupement_line_length.label('heb_app_groupement_line_length'),
                              HebergementApp.heb_app_groupement_angle_start.label('heb_app_groupement_angle_start')
                              )
        query = query.join('proprio').outerjoin('epis').join('type').join('app')
        query = query.options(FromCache('gdw'))
        query = query.filter(Hebergement.heb_groupement_pk == pk)
        query = query.filter(sa.and_(Hebergement.heb_site_public == '1',
                                     Proprio.pro_etat == True))
        hebList = []

        for heb in query.all():
            heb_type_translated = translate(_(heb.heb_type),
                                            context=self.request)
            heb_type_type_translated = translate(_(heb.heb_type_type),
                                                 context=self.request)
            hebList.append({
                'heb_pk': heb.heb_pk,
                'heb_nom': heb.heb_nom,
                'type_heb': heb.heb_type_type,
                'type_heb_title': heb_type_type_translated,
                'heb_type': heb.heb_type,
                'heb_type_trad': heb_type_translated,
                'heb_type_code': heb.heb_type_code,
                'heb_code_gdw': heb.heb_code_gdw,
                'heb_localite': heb.heb_localite,
                'heb_nombre_epis': heb.heb_nombre_epis,
                'heb_cgt_cap_min': heb.heb_cgt_cap_min,
                'heb_cgt_cap_max': heb.heb_cgt_cap_max,
                'heb_cgt_nbre_chmbre': heb.heb_cgt_nbre_chmbre,
                'heb_fumeur': self._get_metadata('heb_fumeur', heb.heb_pk),
                'heb_animal': self._get_metadata('heb_animal', heb.heb_pk),
                'url_heb': self._get_url(heb.heb_pk)})
        return json.dumps(hebList)

    def _get_metadata(self, metadata_id, heb_pk):
        from gites.db import session
        from gites.db.content.hebergement.linkhebergementmetadata import LinkHebergementMetadata
        session = session()
        query = session.query(LinkHebergementMetadata.link_met_value)
        query = query.options(FromCache('gdw'))
        query = query.join('hebergement').join('metadata_info')
        query = query.filter(Hebergement.heb_pk == heb_pk)
        return query.filter(Metadata.met_id == metadata_id).scalar()

    def _get_url(self, pk):
        context = Hebergement.first(heb_pk=pk)
        portal = api.portal.get()
        container = portal.hebergement
        commune = context.commune.com_id
        language = self.request.get('LANGUAGE', 'en')
        typeHeb = context.type.getId(language)
        hebId = context.heb_id
        return "%s/%s/%s/%s" % (container.absolute_url(),
                                typeHeb,
                                commune,
                                hebId,
                                )

    def get_tarif_table(self, section=None):
        """
        Return render of tarif table
        """
        table = tarif.TarifTable(
            self.context,
            self.request,
            self.context.heb_pk,
            section)

        if section in ['OTHER', 'CHARGES', 'ROOM', 'CHRISTMAS', 'FEAST_WEEKEND']:
            zope.interface.alsoProvides(
                table, interfaces.ITarifDisplaySubtype)
        else:
            zope.interface.alsoProvides(
                table, interfaces.ITarifDisplayType)
        zope.interface.alsoProvides(
            table, interfaces.ITarifDisplayTable)

        table.update()
        return table.render()

    def heb_url(self):
        url = 'http://%s' % self.context.heb_url
        portal_url = api.portal.get().absolute_url()
        if portal_url.startswith('https'):
            portal_url = 'http%s' % portal_url[5:]
        return '%(base)s/@@l?u=%(url)s&m=%(md5)s' % {
            'base': portal_url,
            'url': urllib.quote(url),
            'md5': self.heb_url_md5(url),
        }

    def heb_url_md5(self, url):
        """Return the md5 associated to the hebergement url"""
        return utils.calculate_md5(url)


class HebergementIconsView(BrowserView):
    """
    View for the icons of an hebergement
    """
    implements(IHebergementIconsView)

    def getSignaletiqueUrl(self):
        """
        return the url of the signaletique
        """
        url = getToolByName(self.context, 'portal_url')()
        translate = queryMultiAdapter((self.context, self.request),
                                      name='getTranslatedObjectUrl')
        if self.context.type.type_heb_code in ['CH', 'MH', 'CHECR']:
            url = translate('signaletiques/signaletique-chambre-hote')
        else:
            url = translate('signaletiques/signaletique-gite')
        return url

    def getEpisIcons(self, number):
        result = []
        url = getToolByName(self.context, 'portal_url')()
        if self.context.type.type_heb_code in ['MV']:
            for i in range(number):
                result.append('<img src="1_clef.png" alt="Clef" src="%s1_clef.png"/>' % url)
        else:
            for i in range(number):
                result.append('<img src="1_epis.gif" alt="Epis" src="%s1_epis.gif"/>' % url)
        return " ".join(result)

    def getEpis(self):
        """
        Get the epis icons
        """
        l = [self.getEpisIcons(i.heb_nombre_epis) for i in self.context.epis]
        return " - ".join(l)


class HebergementAbsoluteURL(BrowserView):
    implements(IAbsoluteURL)

    @memoize
    def getHebType(self, typeheb, language):
        from gites.db import session
        session = session()
        typeHeb = session.query(TypeHebergement).filter_by(type_heb_pk=typeheb).first()
        return typeHeb.getId(language)

    def __str__(self):
        if isinstance(self.context, tuple):
            if hasattr(self.context, 'heb_pk'):
                context = Hebergement.first(heb_pk=self.context.heb_pk)
            else:
                return ''
        else:
            context = aq_inner(self.context)
        portal = api.portal.get()
        container = portal.hebergement
        from gites.db import session
        session = session()
        commune = session.query(Commune.com_id).options(FromCache('gdw')).filter_by(com_pk=context.heb_com_fk).first()
        language = self.request.get('LANGUAGE', 'en')
        typeHeb = session.query(TypeHebergement).options(FromCache('gdw')).filter_by(type_heb_pk=context.heb_typeheb_fk).first()
        hebId = context.heb_id
        return "%s/%s/%s/%s" % (container.absolute_url(),
                                #self.getHebType(self.context.heb_typeheb_fk, language),
                                typeHeb.getId(language),
                                commune.com_id,
                                hebId,
                                )

    __call__ = __str__


class HebergementHelper(BrowserView):

    def _get_metadata(self, metadata_id):
        from gites.db import session
        from gites.db.content.hebergement.linkhebergementmetadata import LinkHebergementMetadata
        session = session()
        query = session.query(LinkHebergementMetadata.link_met_value)
        query = query.options(FromCache('gdw'))
        query = query.join('hebergement').join('metadata_info')
        query = query.filter(Hebergement.heb_pk == self.context.heb_pk)
        return query.filter(Metadata.met_id == metadata_id).scalar()

    def is_smoker(self):
        """
        """
        return self._get_metadata('heb_fumeur')

    def accept_dogs(self):
        """
        """
        return self._get_metadata('heb_animal')
