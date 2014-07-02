# encoding: utf-8
"""
gites.core

Created by schminitz
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from zope.publisher.browser import TestRequest

from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

from gites.db.testing import GitesWallonsDBTestCase
from gites.core.testing import GITES_CORE_WITH_ZCML
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID


class TarifsMapperTest(GitesWallonsDBTestCase):
    layer = GITES_CORE_WITH_ZCML
    gites_wallons_sql_file = ('tarifs')

    @property
    def _proprio_hebs_vocabulary(self):
        items = []
        items.append(SimpleTerm(81, 81, u'81 - La turbine'))
        return SimpleVocabulary(items)

    def setUp(self):
        from gites.core.browser.tarif_edition import TarifEditionView
        request = TestRequest()
        self.view = TarifEditionView(object(), request)

    def test_validate_good_value(self):
        self.view.request = TestRequest(
            form={'tarif_min_LOW_SEASON': '100',
                  'tarif_max_LOW_SEASON': '200'})

        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])

        result = self.view.validate()
        self.assertTrue(result)

    def test_validate_wrong_value(self):
        self.view.request = TestRequest(
            form={'tarif_min_LOW_SEASON': '100',
                  'tarif_max_LOW_SEASON': 'foo'})

        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])

        result = self.view.validate()
        self.assertFalse(result)

    def test_validate_proprio(self):
        self.view.request = TestRequest(form={'heb_pk': '81'})
        self.mock(self.view,
                  '_get_proprio_hebs',
                  return_value=self._proprio_hebs_vocabulary)

        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Proprietaire'])

        result = self.view.validate()
        self.assertTrue(result)

    def test_validate_wrong_role(self):
        result = self.view.validate()
        self.assertFalse(result)
