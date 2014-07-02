# encoding: utf-8
"""
gites.core

Created by schminitz
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
import transaction

from zope.publisher.browser import TestRequest

from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

from gites.db.content import Tarifs
from gites.db.testing import GitesWallonsDBTestCase
from gites.core.testing import GITES_CORE_WITH_ZCML
from plone.app.testing import login
from plone.app.testing import logout
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

    def tearDown(self):
        super
        logout()

    def test_validate_good_value(self):
        self.view.request = TestRequest(
            form={'tarif_min_LOW_SEASON_WEEK': '100',
                  'tarif_max_LOW_SEASON_WEEK': '200'})

        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])

        result = self.view.validate()
        self.assertTrue(result)

    def test_validate_wrong_value(self):
        self.view.request = TestRequest(
            form={'tarif_min_LOW_SEASON_WEEK': '100',
                  'tarif_max_LOW_SEASON_WEEK': 'foo'})

        portal = self.layer['portal']
        login(portal, 'manager')

        result = self.view.validate()
        self.assertFalse(result)

    def test_validate_proprio(self):
        self.view.request = TestRequest(form={'heb_pk': '81'})
        self.mock(self.view,
                  '_get_proprio_hebs',
                  return_value=self._proprio_hebs_vocabulary)

        portal = self.layer['portal']
        login(portal, 'proprio')

        result = self.view.validate()
        self.assertTrue(result)

    def test_validate_wrong_role(self):
        result = self.view.validate()
        self.assertFalse(result)

    def test_apply_tarifs_changes(self):
        tarifs = Tarifs.get_hebergement_tarifs(81)
        tarif_pk = tarifs[0].pk
        self.assertEqual(len(tarifs), 1)
        self.assertEqual(tarifs[0].min, 50)
        self.assertEqual(tarifs[0].max, 60)

        # New values given
        self.view.request = TestRequest(
            form={'tarif_min_LOW_SEASON_WEEK': '100',
                  'tarif_max_LOW_SEASON_WEEK': '200',
                  'tarif_heb_pk': 81})
        portal = self.layer['portal']
        login(portal, 'manager')

        self.view.apply_tarifs_changes()
        transaction.commit()

        # New line inserted with new values
        tarifs = Tarifs.get_hebergement_tarifs(81)
        self.assertTrue(len(tarifs) > 1)
        for tarif in tarifs:
            if tarif.type == 'LOW_SEASON' and tarif.subtype == 'WEEK':
                self.assertNotEqual(tarif.pk, tarif_pk)
                self.assertEqual(tarif.min, 100)
                self.assertEqual(tarif.max, 200)
                self.assertEqual(tarif.valid, True)

    def test_apply_tarifs_changes_no_heb(self):
        tarifs = Tarifs.get_hebergement_tarifs(81)
        tarif_pk = tarifs[0].pk
        self.assertEqual(len(tarifs), 1)
        self.assertEqual(tarifs[0].min, 50)
        self.assertEqual(tarifs[0].max, 60)

        # No heb given
        self.view.request = TestRequest(
            form={'tarif_min_LOW_SEASON_WEEK': '100',
                  'tarif_max_LOW_SEASON_WEEK': '200'})

        self.view.apply_tarifs_changes()
        transaction.commit()

        # Nothing changes
        tarifs = Tarifs.get_hebergement_tarifs(81)
        for tarif in tarifs:
            if tarif.type == 'LOW_SEASON' and tarif.subtype == 'WEEK':
                self.assertEqual(tarif.pk, tarif_pk)
                self.assertEqual(tarif.min, 50)
                self.assertEqual(tarif.max, 60)

    def test_apply_tarifs_changes_exist(self):
        """
        cf if to_confirm_exist: in tarif_edition
        """
        tarifs = Tarifs.get_hebergement_tarifs(81)
        tarif_pk = tarifs[0].pk
        self.assertEqual(len(tarifs), 1)
        self.assertEqual(tarifs[0].min, 50)
        self.assertEqual(tarifs[0].max, 60)

        # Same values given
        self.view.request = TestRequest(
            form={'tarif_min_LOW_SEASON_WEEK': '50',
                  'tarif_max_LOW_SEASON_WEEK': '60',
                  'tarif_heb_pk': 81})

        # No new line inserted
        self.view.apply_tarifs_changes()
        transaction.commit()

        tarifs = Tarifs.get_hebergement_tarifs(81)
        for tarif in tarifs:
            if tarif.type == 'LOW_SEASON' and tarif.subtype == 'WEEK':
                self.assertEqual(tarif.pk, tarif_pk)
                self.assertEqual(tarif.min, 50)
                self.assertEqual(tarif.max, 60)
