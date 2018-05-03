# -*- coding: utf-8 -*-
from poi.pas.saml2.testing import POIPASSAML2_PLONE_INTEGRATION_TESTING

import unittest


class TestPluginUsersGroupProvider(unittest.TestCase):

    layer = POIPASSAML2_PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.aclu = self.portal.acl_users

        # add poipas.group behavior to folder for testing purposes
        ftype = self.portal.portal_types.Folder
        behaviors = list(ftype.getProperty('behaviors'))
        behaviors.append('poipas.group')
        ftype.manage_changeProperties(behaviors=tuple(behaviors))

    def _make_group(self, newid):
        pass

    def test_group_ids(self):
        # TODO
        pass

    def test_group_info(self):
        # TODO
        pass

    def test_group_infos(self):
        # TODO
        pass
