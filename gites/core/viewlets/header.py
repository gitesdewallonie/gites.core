# -*- coding: utf-8 -*-
from five import grok
from zope import interface

from gites.core.browser.search import BasicForm


grok.templatedir('templates')
grok.context(interface.Interface)


class HeaderViewletManager(grok.ViewletManager):
    grok.name('gites.header')


class TopHeaderViewlet(grok.Viewlet):
    grok.order(10)


class MainHeaderViewlet(grok.Viewlet):
    grok.order(20)

    def update(self):
        self.form = BasicForm(self.context, self.request)
        self.form.update()

        # Defines the placeholder for some field
        widgets_placeholder = ('fromDate', 'toDate', 'nearTo')
        for widget in self.form.widgets:
            if widget in widgets_placeholder:
                label = self.form.widgets[widget].label
                self.form.widgets[widget].placeholder = label


# register all viewlets in this viewlet manager:
grok.viewletmanager(HeaderViewletManager)
