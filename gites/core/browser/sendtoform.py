# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from zope.interface import implements
from ZODB.POSException import ConflictError

from gites.core.browser.interfaces import ISendToFormView
from gites.db.interfaces import IHebergement


class SendToFormView(BrowserView):
    """
    """
    implements(ISendToFormView)

    def __init__(self, context, request):
        super(SendToFormView, self).__init__(context, request)
        super(BrowserView, self).__init__(context, request)

    def validateAndSend(self):
        errors, gotErrors = self.validate()

        if self.request.get('form.submitted') and not gotErrors:
            self.sendMailAndRedirect()

        return errors

    def validate(self):
        """Validate sendto_form"""

        errors = {'send_to_address': '',
                  'send_from_address': ''}
        gotErrors = False

        if not self.request.get('form.submitted'):
            return errors, gotErrors

        plone_utils = self.context.plone_utils
        send_to_address = self.request.get('send_to_address')
        send_from_address = self.request.get('send_from_address')

        if not send_to_address:
            errors['send_to_address'] = _(u'Please submit an email address.')
            gotErrors = True
        elif not plone_utils.validateEmailAddresses(send_to_address):
            errors['send_to_address'] = _(u'Please submit a valid email address.')
            gotErrors = True

        if not send_from_address:
            errors['send_from_address'] = _(u'Please submit an email address.')
            gotErrors = True
        elif not plone_utils.validateSingleEmailAddress(send_from_address):
            errors['send_from_address'] = _(u'Please submit a valid email address.')
            gotErrors = True

        return errors, gotErrors

    def sendMailAndRedirect(self):
        """"""
        plone_utils = self.context.plone_utils
        pretty_title_or_id = plone_utils.pretty_title_or_id
        site = getToolByName(self.context, 'portal_url').getPortalObject()

        variables = {
            'send_to_address': self.request.get('send_to_address'),
            'send_from_address': self.request.get('send_from_address'),
            'subject': pretty_title_or_id(self.context),
            'url': self.request.get('ACTUAL_URL').replace('/gdw_sendto_form', ''),
            'title': pretty_title_or_id(self.context),
            'description': self.getDescription(),
            'comment': self.request.get('comment', None),
            'envelope_from': site.getProperty('email_from_address'),
        }

        try:
            plone_utils.sendto(**variables)
        except ConflictError:
            raise
        except:
            exception = plone_utils.exceptionString()
            message = _(u'Unable to send mail: ${exception}',
                        mapping={u'exception': exception})
            plone_utils.addPortalMessage(message, 'error')
            variables['url'] = self.request.get('ACTUAL_URL')

        self.context.REQUEST.RESPONSE.redirect(variables['url'])

    def getDescription(self):
        if IHebergement.providedBy(self.context):
            language = self.request.get('LANGUAGE', 'en')
            description = self.context.getDescription(language)
        else:
            description = self.context.Description()
        return description
