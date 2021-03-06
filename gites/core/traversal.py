# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
import re
from zope.publisher.interfaces.http import IHTTPRequest
from zope.component import adapts, getMultiAdapter, queryMultiAdapter
from zope.app.publisher.browser import getDefaultViewName
from ZPublisher.BaseRequest import DefaultPublishTraverse
from Products.CMFPlone.interfaces import IPloneSiteRoot
from gites.core.interfaces import IHebergementFolder
from affinitic.db.cache import FromCache
from z3c.sqlalchemy import getSAWrapper
from zExceptions import NotFound


def isInt(name):
    m = re.compile(r'^([+-])?\d+$')
    return bool(m.match(name))


class RootFolderTraversable(DefaultPublishTraverse):
    """
    """
    adapts(IPloneSiteRoot, IHTTPRequest)

    def publishTraverse(self, request, name):
        """
        Directly traverse to an accommodation if a PK is specified in URL
        """
        if isInt(name):
            hebPk = int(name)
            wrapper = getSAWrapper('gites_wallons')
            session = wrapper.session
            Hebergement = wrapper.getMapper('hebergement')
            heb = session.query(Hebergement).options(FromCache('gdw')).get(hebPk)
            if heb and int(heb.heb_site_public) == 1 and heb.proprio.pro_etat:
                hebURL = getMultiAdapter((heb.__of__(self.context.hebergement),
                                          request), name="url")
                request.response.redirect(str(hebURL))
                return ''
        return super(RootFolderTraversable, self).publishTraverse(request, name)


class HebergementFolderTraversable(DefaultPublishTraverse):
    """
    """
    adapts(IHebergementFolder, IHTTPRequest)

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
        if name not in self.context.known_types_id:
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
        if name.startswith('@@'):
            # A view has explicitly been requested, so make that the
            # view_name (stripping off the leading @@ which causes view
            # lookups to fail otherwise).
            view_name = name[2:]
        else:
            # last name is another keyword
            keywords.append(name)

        #if len(keywords) == 0:
            # No keywords given, just a view specified. Create a view for the
            # topic container.
        #    context = self.context
        #else:
        return self.getContext(name, keywords, view_name)

    def getHebergementByPk(self, heb_pk):
        """
        retourne un hebergement selon sa pk
        table hebergement
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        Hebergement = wrapper.getMapper('hebergement')

        return session.query(Hebergement).options(FromCache('gdw')).get(heb_pk)

    def getDefaultViewForObject(self, obj, view_name):
        obj = obj.__of__(self.context)
        view_name = view_name or getDefaultViewName(obj, self.request,
                                                    self.context)
        view = getMultiAdapter((obj, self.request), name=view_name)
        return view.__of__(self.context)

    def getContext(self, name, sub, view_name):
        if isInt(name):
            context = self.getHebergementByPk(int(name))
            if context is None:
                raise NotFound
            return self.getDefaultViewForObject(context, view_name)
        lenSub = len(sub)
        if sub:
            if (lenSub == 1 and sub[0] in self.context.known_types_id) or \
               (lenSub == 2 and sub[0] in self.context.known_types_id and \
                sub[1] in ['update_listing', 'update_map_listing']):
                # /hebergement/gites/
                #              NAME
                # affichage type de gites
                wrapper = getSAWrapper('gites_wallons')
                session = wrapper.session
                typeHeb = self.context.known_types_id.get(sub[0])
                TypeHebs = wrapper.getMapper('type_heb')
                typeHeb = session.query(TypeHebs).get(int(typeHeb))
                typeHeb = typeHeb.__of__(self.context)
                name = 'index.html'
                if lenSub == 2:
                    name = sub[1]
                return queryMultiAdapter((typeHeb,
                                          self.request),
                                          name=name)

            if (lenSub == 2 and sub[1] in self.context.known_communes_id \
                and sub[0] in self.context.known_types_id) or \
               (lenSub == 3 and sub[1] in self.context.known_communes_id \
                and sub[0] in self.context.known_types_id and \
                sub[2] in ['update_listing', 'update_map_listing']):
                # /hebergement/gites/villlers/
                #              NAME * SUB[0]
                # affichage type de gites pour ville
                wrapper = getSAWrapper('gites_wallons')
                session = wrapper.session
                typeHeb = self.context.known_types_id.get(sub[0])
                commune = self.context.known_communes_id.get(sub[1])
                Commune = wrapper.getMapper('commune')
                TypeHebs = wrapper.getMapper('type_heb')
                typeHeb = session.query(TypeHebs).get(int(typeHeb))
                commune = session.query(Commune).get(int(commune))
                typeHeb = typeHeb.__of__(self.context)
                name = 'index.html'
                if lenSub == 3:
                    name = sub[2]
                return queryMultiAdapter((commune.__of__(typeHeb),
                                        self.request),
                                        name=name)

            elif lenSub >= 3 and \
                    sub[1] in self.context.known_communes_id \
                    and sub[0] in self.context.known_types_id \
                    and sub[2] in self.context.known_gites_id:
                # /hebergement/gites/villlers/les-roches
                #              NAME * SUB[0]* SUB[1]
                # affichage d un gite
                if lenSub > 3:
                    page = name
                    name = sub[-2]
                pk = self.context.known_gites_id.get(name, None)
                hebergement = self.getHebergementByPk(int(pk))
                if lenSub == 3:
                    return self.getDefaultViewForObject(hebergement, view_name)
                else:
                    return queryMultiAdapter((hebergement.__of__(self.context),
                                              self.request), name=page).__of__(self.context)
        raise NotFound

    def nextName(self):
        """Pop the next name off of the traversal stack.
        """
        return self.request['TraversalRequestNameStack'].pop()

    def hasMoreNames(self):
        """Are there names left for traversal?
        """
        return len(self.request['TraversalRequestNameStack']) > 0
