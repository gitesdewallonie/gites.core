# -*- coding: utf-8 -*-
from datetime import date
from mailer import Mailer
from smtplib import SMTPSenderRefused
import time

from collective.captcha.browser.captcha import Captcha
from Products.CMFDefault.exceptions import EmailAddressInvalid
from Products.CMFDefault.utils import checkEmailAddress
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from z3c.sqlalchemy import getSAWrapper
from zope.component import queryMultiAdapter
from zope.interface import implements

from gites.locales import GitesMessageFactory as _
from interfaces import ISendMail

LANG_MAP = {'en': 'Anglais',
            'fr': 'Français',
            'nl': 'Néerlandais',
            'de': 'Allemand'}


class SendMail(BrowserView):
    """
    Envoi de mail
    """
    implements(ISendMail)

    def sendBlogSubscriptionMail(self):
        """
        envoi des informations d'inscription à la newsletter du blog
        """
        nom = self.request.get('nom', '')
        email = self.request.get('email', '')
        fromMail = "info@gitesdewallonie.be"
        if not email:
            return
        try:
            checkEmailAddress(email)
        except EmailAddressInvalid:
            return
        mailer = Mailer("localhost", fromMail)
        mailer.setSubject("[INSCRIPTION NEWSLETTER BLOG]")
        mailer.setRecipients("michael@gitesdewallonie.be")
        mail = u""":: INSCRIPTION ::

Une demande d'inscription a été envoyée via le blog :

    * Nom : %s
    * Email : %s
""" \
           %(unicode(nom, 'utf-8'), \
             unicode(email, 'utf-8'))
        mailer.sendAllMail(mail.encode('utf-8'), plaintext=True)

    def sendMailToProprio(self):
        """
        envoi d'un mail au proprio suite a un contact via hebergement description
        """
        hebPk = self.request.get('heb_pk')
        captcha = self.request.get('captcha', '')
        captchaView = Captcha(self.context, self.request)
        isCorrectCaptcha = captchaView.verify(captcha)
        if not isCorrectCaptcha:
            return self()

        dateDebutStr = self.request.get('fromDate')
        dateFinStr = self.request.get('toDate')
        if dateDebutStr and dateFinStr:
            try:
                dateDebut = date.fromtimestamp(time.mktime(time.strptime(dateDebutStr, '%d/%m/%Y')))
                dateFin = date.fromtimestamp(time.mktime(time.strptime(dateFinStr, '%d/%m/%Y')))
            except ValueError:
                self.request['fromDate'] = 'error'
                self.request['toDate'] = ''
                self.request['captcha'] = ''
                return self()
            else:
                if dateDebut >= dateFin:
                    self.request['fromDate'] = 'error'
                    self.request['toDate'] = ''
                    self.request['captcha'] = ''
                    return self()
        else:
            if dateDebutStr or dateFinStr:
                # une seule date a été remplie
                self.request['fromDate'] = 'error'
                self.request['toDate'] = ''
                self.request['captcha'] = ''
                return self()

        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        Hebergement = wrapper.getMapper('hebergement')
        heb = session.query(Hebergement).get(int(hebPk))
        hebNom = heb.heb_nom
        proprioMail = heb.proprio.pro_email
        if not proprioMail:
            proprioMail = u'info@gitesdewallonie.be'
        contactCivilite = self.request.get('contactCivilite')
        contactNom = self.request.get('contactNom', '')
        contactPrenom = self.request.get('contactPrenom', '')
        contactAdresse = self.request.get('contactAdresse', '')
        contactCp = self.request.get('contactCp')
        contactLocalite = self.request.get('contactLocalite', '')
        contactPays = self.request.get('contactPays', '')
        contactLangue = self.request.get('contactLangue', None)
        if not contactLangue or contactLangue.strip() == '...':
            language = self.request.get('LANGUAGE', 'en')
            contactLangue = LANG_MAP.get(language, '')
        contactTelephone = self.request.get('contactTelephone', '')
        contactFax = self.request.get('contactFax', '')
        contactEmail = self.request.get('contactEmail', None)
        nombrePersonne = self.request.get('nombrePersonne')
        remarque = self.request.get('remarque', '')

        fromMail = "info@gitesdewallonie.be"
        if contactEmail is not None:
            try:
                checkEmailAddress(contactEmail)
                fromMail = contactEmail
            except EmailAddressInvalid:
                pass

        mailer = Mailer("localhost", fromMail)
        mailer.setSubject("[DEMANDE D'INFORMATION PAR LE SITE DES GITES DE WALLONIE]")
        mailer.setRecipients(proprioMail)
        mail = u""":: DEMANDE D'INFORMATION ::

Une demande d'information vient d'être réalisée via le site des Gîtes de Wallonie pour %s (référence %s).

Il s'agit de :

    * Civilité : %s
    * Nom : %s
    * Prénom : %s
    * Adresse : %s
    * Localité : %s %s
    * Pays : %s
    * Langue : %s
    * Téléphone : %s
    * Fax : %s
    * E-mail : %s
    * Date début séjour  : %s
    * Date fin séjour  : %s
    * Nombre de personnes : %s
    * Remarque : %s
""" \
              % (hebNom, \
                hebPk, \
                contactCivilite, \
                unicode(contactNom, 'utf-8'), \
                unicode(contactPrenom, 'utf-8'), \
                unicode(contactAdresse, 'utf-8'), \
                contactCp, \
                unicode(contactLocalite, 'utf-8'), \
                unicode(contactPays, 'utf-8'), \
                unicode(contactLangue, 'utf-8'), \
                contactTelephone, \
                contactFax, \
                unicode(contactEmail, 'utf-8'), \
                dateDebutStr, \
                dateFinStr, \
                nombrePersonne,\
                unicode(remarque, 'utf-8'))
        mailer.sendAllMail(mail.encode('utf-8'), plaintext=True)

        translate = queryMultiAdapter((self.context, self.request),
                                       name='getTranslatedObjectUrl')

        if self.request.get('newsletter', False):
            url = translate('newsletter')
            self.request.RESPONSE.redirect(url)
        else:
            url = translate('mailsent')
            self.request.RESPONSE.redirect(url)
        return ''

    def sendMailForProblem(self):
        """
        envoi d'un mail pour signaler un problème
        """
        if self.request.get('vecteur') is None:
            return
        captcha = self.request.get('captcha', '')
        captchaView = Captcha(self.context, self.request)
        isCorrectCaptcha = captchaView.verify(captcha)
        if not isCorrectCaptcha:
            return ""

        gdwMail = u'info@gitesdewallonie.be'
        typeProbleme = self.request.get('typeProbleme', None)
        if not typeProbleme or typeProbleme.strip() == '...':
            typeProbleme = u'Non spécifié'
        elif typeProbleme == "autre":
            typeProbleme = self.request.get('typeautre')
        contactNom = self.request.get('contactNom', '')
        contactPrenom = self.request.get('contactPrenom', '')
        contactLangue = self.request.get('contactLangue', None)
        if not contactLangue or contactLangue.strip() == '...':
            language = self.request.get('LANGUAGE', 'en')
            contactLangue = LANG_MAP.get(language, '')
            contactLangue = contactLangue.decode('utf-8')
        contactEmail = self.request.get('contactEmail', None)
        hebPk = self.request.get('heb_pk', '')
        remarque = self.request.get('remarque', '')

        fromMail = "info@gitesdewallonie.be"
        if contactEmail is not None:
            try:
                checkEmailAddress(contactEmail)
                fromMail = contactEmail
            except EmailAddressInvalid:
                pass

        mailer = Mailer("localhost", fromMail)
        mailer.setSubject("[SIGNALER UN PROBLEME PAR LE SITE DES GITES DE WALLONIE]")
        mailer.setRecipients(gdwMail)
        mail = """:: SIGNALER UN PROBLEME ::

L'utilisateur %s %s signale un problème sur le site des Gîtes de Wallonie.

Il s'agit de :

    * Nom : %s
    * Prénom : %s
    * Langue : %s
    * E-mail : %s
    * Hébergement concerné : %s
    * Type de problème : %s
    * Remarque : %s
""" \
            % (unicode(contactNom).encode('utf-8'), \
              unicode(contactPrenom).encode('utf-8'), \
              unicode(contactNom).encode('utf-8'), \
              unicode(contactPrenom).encode('utf-8'), \
              unicode(contactLangue).encode('utf-8'), \
              unicode(contactEmail).encode('utf-8'), \
              unicode(hebPk).encode('utf-8'), \
              unicode(typeProbleme).encode('utf-8'), \
              unicode(remarque).encode('utf-8'))
        try:
            mailer.sendAllMail(mail, plaintext=True)
        except SMTPSenderRefused:
            messages = IStatusMessage(self.request)
            messages.add(_(u"Il y a eu un problème lors de l'envoi de votre demande."), type=u"error")
            return

        translate = queryMultiAdapter((self.context, self.request),
                                       name='getTranslatedObjectUrl')

        url = translate('mailsent')
        self.request.RESPONSE.redirect(url)
        return ''
