# -*- coding: utf-8 -*-
from poi.pas.saml2.testing import POIPASSAML2_ZOPE_FIXTURE

import unittest


class TestPluginForGroupCapability(unittest.TestCase):
    """interface plonepas_interfaces.capabilities.IGroupCapability

    Test if above interface works as expected
    """

    layer = POIPASSAML2_ZOPE_FIXTURE

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.aclu = self.layer['app'].acl_users

    def test_addplugin_users(self):
        PLUGINID = 'poisaml2test'
        from poi.pas.saml2.setuphandlers import _add_plugin
        from poi.pas.saml2.plugins.users import PoiUsersPlugin
        result = _add_plugin(self.aclu, PLUGINID, 'Users', PoiUsersPlugin)
        self.assertIs(result, None)
        self.assertIn(PLUGINID, self.aclu.objectIds())

        poisaml2 = self.aclu[PLUGINID]
        self.assertIsInstance(poisaml2, PoiUsersPlugin)

        result = _add_plugin(self.aclu, PLUGINID, 'Users', PoiUsersPlugin)
        self.assertEqual(result, 'Users already installed.')


    def test_removeplugin_users(self):
        # add before remove
        PLUGINID = 'poisaml2test'
        from poi.pas.saml2.setuphandlers import _add_plugin
        from poi.pas.saml2.plugins.users import PoiUsersPlugin
        _add_plugin(self.aclu, PLUGINID, 'Users', PoiUsersPlugin)
        self.assertIn(PLUGINID, self.aclu.objectIds())

        # now remove it
        from poi.pas.saml2.setuphandlers import _remove_plugin  # noqa
        _remove_plugin(self.aclu, pluginid=PLUGINID)

        self.assertNotIn(PLUGINID, self.aclu.objectIds())

