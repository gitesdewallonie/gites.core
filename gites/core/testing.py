# -*- coding: utf-8 -*-
"""
gites.core

Created by schminitz
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

from plone.app.testing import PLONE_INTEGRATION_TESTING
from plone.testing import Layer
from plone.testing import zca

import gites.core
from gites.db.testing import PGRDB


class GitesCoreLayer(Layer):
    defaultBases = (PLONE_INTEGRATION_TESTING, PGRDB, )


GITES_CORE = GitesCoreLayer(name='GITES_CORE')


GITES_CORE_WITH_ZCML = zca.ZCMLSandbox(bases=(GITES_CORE, ),
                                       filename="testing.zcml",
                                       package=gites.core,
                                       name='GITES_CORE_WITH_ZCML')
