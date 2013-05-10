# -*- coding: utf-8 -*-
from zope.interface import implements
from zope.component import getUtility

from collective.opengraph.viewlets import ATMetatags, decode_str, LastUpdatedOrderedDict
from collective.opengraph.interfaces import IOpengraphMetatags

from affinitic.pwmanager.interfaces import IPasswordManager


class GdwATMetatags(ATMetatags):
    """
    Facebook informations for gdw
    """

    implements(IOpengraphMetatags)

    @property
    def admins(self):
        pwManager = getUtility(IPasswordManager, 'facebookadmins')
        admins = self.settings.admins or pwManager.username
        return decode_str(admins, self.default_charset)

    @property
    def app_id(self):
        pwManager = getUtility(IPasswordManager, 'facebookapp')
        appid = self.settings.app_id or pwManager.username
        return decode_str(appid, self.default_charset)

    @property
    def content_type(self):
        return decode_str('hotel', self.default_charset)


class BoutiqueItemATMetatags(ATMetatags):
    """
    Boutique item Facebook informations
    """

    implements(IOpengraphMetatags)

    @property
    def image_url(self):
        return self.context.photo.absolute_url()


class HebergementATMetatags(ATMetatags):
    """
    Boutique item Facebook informations
    """

    implements(IOpengraphMetatags)

    @property
    def metatags(self):
        """
        Override to change the url metatag
        """
        tags = LastUpdatedOrderedDict()
        tags.update([('og:title', self.title),
                     ('og:url', self.url),
                     ('og:image', self.image_url),
                     ('og:site_name', self.sitename),
                     ('og:description', self.description)])
        if self.content_type:
            tags.update({'og:type': self.content_type})
        if self.admins:
            tags.update({'fb:admins': self.admins})
        if self.app_id:
            tags.update({'fb:app_id': self.app_id})
        return tags

    @property
    def title(self):
        return self.context.Title()

    @property
    def url(self):
        return self.context.getUrl()

    @property
    def image_url(self):
        url = self.context.photos_heb.absolute_url()
        image_url = '%s/%s' % (url, self.context.getVignette())
        return image_url

    @property
    def description(self):
        language = self.portal_state.request.get('LANGUAGE', 'en')
        return self.context.getDescription(language)
