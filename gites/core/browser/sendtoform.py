from Products.Five import BrowserView
from zope.interface import alsoProvides, implements
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from gites.core.interfaces import IMapRequest
from gites.core.browser.interfaces import ISendToFormView


class SendToFormView(BrowserView):
    """
    """
    implements(ISendToFormView)

    def __init__(self, context, request):
        super(SendToFormView, self).__init__(context, request)
        super(BrowserView, self).__init__(context, request)
