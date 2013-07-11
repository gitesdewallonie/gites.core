# encoding: utf-8
"""
gites.core

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

from zope.i18n.format import DateTimeParseError
from z3c.form.converter import FormatterValidationError


def date_update(self):
    super(self.__class__, self).update()
    self.placeholder = getattr(self, 'placeholder', '')


def date_converter(self, value):
    """ See collective.z3cform.datepicker.widget.DateConverter """
    if value == u'':
        return self.field.missing_value
    try:
        return self.formatter.parse(value, pattern="dd/MM/yyyy")
    except DateTimeParseError, err:
        raise FormatterValidationError(err.args[0], value)
