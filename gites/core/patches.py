# -*- coding: utf-8 -*-
from ZPublisher.HTTPRequest import HTTPRequest
from Products.PloneLanguageTool.LanguageTool import LanguageTool


LanguageTool._old___call__ = LanguageTool.__call__


def LanguageTool__call__(self, container, req):
    """The __before_publishing_traverse__ hook.

    Patched to *not* set the language cookie, as this breaks the site model.

    """
    self._old___call__(container, req)
    if not isinstance(req, HTTPRequest):
        return None
    response = req.response
    if 'I18N_LANGUAGE' in response.cookies:
        if 'set_language' in req.form:
            return None
        del response.cookies['I18N_LANGUAGE']

LanguageTool.__call__ = LanguageTool__call__
