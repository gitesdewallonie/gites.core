# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
import re
from zope.publisher.interfaces.http import IHTTPRequest
from zope.component import adapts, getMultiAdapter
from zope.app.publisher.browser import getDefaultViewName
from ZPublisher.BaseRequest import DefaultPublishTraverse
from gites.core.interfaces import IHebergementFolder
from z3c.sqlalchemy import getSAWrapper
from zExceptions import NotFound


class HebergementFolderTraversable(DefaultPublishTraverse):
    """
    """
    adapts(IHebergementFolder, IHTTPRequest)

    def isInt(self, name):
        m = re.compile(r'^([+-])?\d+$')
        return bool(m.match(name))

    def getHebergementByPk(self, heb_pk):
        """
        retourne un hebergement selon sa pk
        table hebergement
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        Hebergement = wrapper.getMapper('hebergement')
        return session.query(Hebergement).get(heb_pk)

    def publishTraverse(self, request, name):
        """Interpret any remaining names on the traversal stack as keywords
        of this topic container. Only exception is an appended view name at
        the end of the traversal stack, or if a sub-class aborts the process

        This operation will empty the traversal stack! While the view have
        an instance of ``klass`` as context, it will have the topic container
        as acquistion parent! The ``klass`` instance will be initialized with
        the keywords taken from the traversal stack.
        """
        # The first name might denote a content object to be acquired,
        # e.g. an image. In that case we're done.
        try:
            return super(HebergementFolderTraversable,
                         self).publishTraverse(request, name)
        except AttributeError:
            pass

        self.request = request

        # collect keywords
        keywords = []
        while self.hasMoreNames():
            keywords.append(name)
            name = self.nextName()
        # Determine view
        view_name = None
        context = None
        if name.startswith('@@'):
            # A view has explicitly been requested, so make that the
            # view_name (stripping off the leading @@ which causes view
            # lookups to fail otherwise).
            view_name = name[2:]
        else:
            # last name is another keyword
            keywords.append(name)

        if len(keywords) == 0:
            # No keywords given, just a view specified. Create a view for the
            # topic container.
            context = self.context
        else:
            if self.isInt(name):
                context = self.getHebergementByPk(int(name))
                if context is None:
                    raise NotFound
                else:
                    context = context.__of__(self.context)

        view_name = view_name or getDefaultViewName(context, request,
                                                    self.context)
        view = getMultiAdapter((context, request), name=view_name)
        return view.__of__(self.context)

    def nextName(self):
        """Pop the next name off of the traversal stack.
        """
        return self.request['TraversalRequestNameStack'].pop()

    def hasMoreNames(self):
        """Are there names left for traversal?
        """
        return len(self.request['TraversalRequestNameStack']) > 0
