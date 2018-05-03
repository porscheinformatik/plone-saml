# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from poi.pas.saml2.testing import POIPASSAML2_PLONE_INTEGRATION_TESTING

import unittest


class TestSetup(unittest.TestCase):
    """Test that poi.pas.saml2 is properly installed."""

    layer = POIPASSAML2_PLONE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if poi.pas.saml2 is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'poi.pas.saml2'))

    def test_browserlayer(self):
        """Test that IPoiPasSaml2Layer is registered."""
        from poi.pas.saml2.interfaces import (
            IPoiPasSaml2Layer)
        from plone.browserlayer import utils
        self.assertIn(IPoiPasSaml2Layer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = POIPASSAML2_PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['poi.pas.saml2'])

    def test_product_uninstalled(self):
        """Test if poi.pas.saml2 is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'poi.pas.saml2'))

    def test_browserlayer_removed(self):
        """Test that IPoiPasSaml2Layer is removed."""
        from poi.pas.saml2.interfaces import IPoiPasSaml2Layer
        from plone.browserlayer import utils
        self.assertNotIn(IPoiPasSaml2Layer, utils.registered_layers())
