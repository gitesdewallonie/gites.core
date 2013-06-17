""" Override the default Plone layout utility.
"""

from zope.component import queryUtility
from zope.component import getMultiAdapter

from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.app.layout.globals import layout as base
from plone.app.layout.navigation.interfaces import INavigationRoot

from gites.db.interfaces import IHebergement


class LayoutPolicy(base.LayoutPolicy):
    """
    Enhanced layout policy helper.

    Extend the Plone standard class to have some more <body> CSS classes
    based on the current context.
    """

    def bodyClass(self, template, view):
        """Returns the CSS class to be used on the body tag.
        """

        # Get content parent
        body_class = base.LayoutPolicy.bodyClass(self, template, view)

        # Include context and parent ids as CSS classes on <body>
        normalizer = queryUtility(IIDNormalizer)

        body_class += " context-" + normalizer.normalize(self.context.getId())

        parent = self.context.aq_parent

        # Check that we have a valid parent
        if hasattr(parent, "getId"):
            body_class += " parent-" + normalizer.normalize(parent.getId())

        # Get path with "Default content item" wrapping applied
        context_helper = getMultiAdapter((self.context, self.request), name="plone_context_state")
        canonical = context_helper.canonical_object()

        # Mark site front page with special CSS class
        if INavigationRoot.providedBy(canonical):

            if "template-document_view" in body_class:
                body_class += " front-page"

        # Add in logged-in / not logged in status
        portal_state = getMultiAdapter((self.context, self.request), name="plone_portal_state")
        if portal_state.anonymous():
            body_class += " anonymous"
        else:
            body_class += " logged-in"

        # See if we are on a room or gites to add a specific CSS class
        if IHebergement.providedBy(self.context):
            hebType = self.context.type.type_heb_type
            if hebType == u'gite':
                body_class += " gite"
            elif hebType == u'chambre':
                body_class += " chambre"

        return body_class
