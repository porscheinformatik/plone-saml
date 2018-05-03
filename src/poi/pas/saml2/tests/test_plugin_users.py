# -*- coding: utf-8 -*-
from poi.pas.saml2.testing import POIPASSAML2_ZOPE_FIXTURE
from poi.pas.saml2.testing import POIPASSAML2_PLONE_INTEGRATION_TESTING

import mock
import unittest
import uuid


def make_user(plugin, userid, password=None, **kwargs):
    plugin._userdata_by_userid[userid] = {
        'userid': userid,
        'secret': password if password else uuid.uuid4(),
    }
    if kwargs:
        plugin._userdata_by_userid[userid].update(kwargs)


class TestPluginUsers(unittest.TestCase):

    layer = POIPASSAML2_ZOPE_FIXTURE

    def setUp(self):
        # create plugin
        from poi.pas.saml2.interfaces import DEFAULT_ID_USERS
        from poi.pas.saml2.plugins.users import PoiUsersPlugin
        from poi.pas.saml2.setuphandlers import _add_plugin
        self.aclu = self.layer['app'].acl_users
        _add_plugin(self.aclu, DEFAULT_ID_USERS, 'Test Users', PoiUsersPlugin)
        self.plugin = self.aclu[DEFAULT_ID_USERS]

    def test_authentication_empty_deny(self):
        credentials = {}
        result = self.plugin.authenticateCredentials(credentials)
        self.assertIsNone(result)

    def test_authentication_nonexistent_deny(self):
        credentials = {
            'login': 'UNSET',
            'password': 'UNSET',
        }
        result = self.plugin.authenticateCredentials(credentials)
        self.assertIsNone(result)

    def test_authentication_user_no_pass_deny(self):
        make_user(self.plugin, 'joe')
        credentials = {
            'login': 'joe',
            'password': 'SECRET',
        }
        result = self.plugin.authenticateCredentials(credentials)
        self.assertIsNone(result)

    def test_authentication_user_same_pass_allow(self):
        make_user(self.plugin, 'joe', password='SECRET')
        credentials = {
            'login': 'joe',
            'password': 'SECRET'
        }
        result = self.plugin.authenticateCredentials(credentials)
        self.assertEqual(result, ('joe', 'joe'))

    def test_user_enumaration_filters(self):
        make_user(self.plugin, '123joe')
        make_user(self.plugin, '123jane')
        make_user(self.plugin, '123wily')
        make_user(self.plugin, '123willi')
        # check by user id
        self.assertEqual(
            [
                {
                    'id': u'123joe',
                    'login': '123joe',
                    'pluginid': 'poisaml2users',
                }
            ],
            self.plugin.enumerateUsers(id='123joe', exact_match=True)
        )
        self.assertEqual(
            [
                {
                    'id': u'123joe',
                    'login': '123joe',
                    'pluginid': 'poisaml2users',
                }
            ],
            self.plugin.enumerateUsers(id='123joe')
        )
        self.assertEqual(
            4,
            len(self.plugin.enumerateUsers(id='123'))
        )
        self.assertEqual(
            2,
            len(self.plugin.enumerateUsers(id='123j'))
        )

        # check by login
        self.assertEqual(
            [
                {
                    'id': u'123joe',
                    'login': '123joe',
                    'pluginid': 'poisaml2users',
                }
            ],
            self.plugin.enumerateUsers(login='123joe', exact_match=True)
        )
        self.assertEqual(
            [
                {
                    'id': u'123joe',
                    'login': '123joe',
                    'pluginid': 'poisaml2users',
                }
            ],
            self.plugin.enumerateUsers(login='123joe')
        )
        self.assertEqual(
            2,
            len(self.plugin.enumerateUsers(login='123j'))
        )
        self.assertEqual(
            2,
            len(self.plugin.enumerateUsers(login='123wil'))
        )
        # list all!

    def test_user_enumeration_all(self):
        make_user(self.plugin, '123joe')
        make_user(self.plugin, '123jane')
        make_user(self.plugin, '123wily')
        make_user(self.plugin, '123willi')
        self.assertEqual(
            4,
            len(self.plugin.enumerateUsers())
        )

