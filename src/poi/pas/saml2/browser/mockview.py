# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from poi.pas.saml2.interfaces import DEFAULT_ID_USERS
from plone import api
from zope.component.hooks import getSite
import logging

logger = logging.getLogger("Plone")

MOCK_NAME_ID = '98031'
SAML_MOCK_DATA = {
    'Authentication.Righttransfer': ['false'],
    'Oragnization.Changed': ['false'],
    'Organization.Address.City': ['Salzburg'],
    'Organization.Address.Country': ['AT'],
    'Organization.Address.PostalCode': ['5020'],
    'Organization.Address.Street': [u'Louise-Pi\xebch-Stra\xdfe 2'],
    'Organization.ID': ['11367'],
    'Organization.Name': ['Porsche Informatik GmbH'],
    'Organization.Types': ['KB', 'DEV', 'IMPORT'],
    'Organization.UID': ['ATU 36773309'],
    'PartnerKey.Brand': ['V'],
    'PartnerKey.Country': ['AT'],
    'PartnerKey.PartnerNumber': ['00101'],
    'Person.AcademicTitle': ['DI'],
    'Person.Brands': ['P', 'A', 'B', 'S', 'C', 'D', 'V', 'G', 'I', 'L'],
    'Person.Email': ['extern.reinhard.pitsch@porscheinformatik.at'],
    'Person.FirstName': ['Reinhard'],
    'Person.Gender': ['1'],
    'Person.LastName': ['Pitsch'],
    'Person.Lastmodified': ['2016-04-22T08:07:18.820Z'],
    'Person.Locale.Date': ['de_AT_EURO'],
    'Person.Locale.Label': ['de_AT_EURO'],
    'Person.Phone': [],
    'Person.Roles': [
        'FU_POI_FREELANCER',
        'FU_POI_ENTW_ALLG',
        'FU_GH_STD_GI_U',
        'FU_HI_SUP',
        'FU_HI_ENTW',
        'TA_T_GH_DEFAULT',
        'TA_T_GH_SCHULUNG',
        'TA_S_ARIS_POI',
        'TA_T_TEF_ANW',
        'TA_ALL',
        'TA_T_GH_GPV_LESEN',
        'TA_T_GH_MPKTVERW',
        'TA_T_STD_MENPKT',
        'TA_HI_SUP',
        'TA_ULINFO_SV',
        'TA_T_GH_HAENDWECHS',
        'TA_POI_ENTW_ALLG',
        'TA_T_BER_KARTANALYS',
        'TA_T_MARKET_INFO'
    ],
    'Person.SalesNumber': [],
    'Portal.ID': ['AT']
}


class _MockSAMLAuth(object):
    def __init__(self):
        self.MOCK_NAME_ID = ''
        self.SAML_MOCK_DATA = {}

    def get_nameid(self):
        return self.MOCK_NAME_ID

    def get_attributes(self):
        return self.SAML_MOCK_DATA

    def get_attribute(self, name):
        return self.SAML_MOCK_DATA[name]

    def set_nameid(self, nid):
        self.MOCK_NAME_ID = nid

    def set_attributes(self, mdata):
        self.SAML_MOCK_DATA = mdata


class MockLoginView(BrowserView):
    def __call__(self):
        mock = _MockSAMLAuth()
        mock.set_attributes(SAML_MOCK_DATA)
        mock.set_nameid(MOCK_NAME_ID)
        plugin = api.portal.get_tool('acl_users')[DEFAULT_ID_USERS]
        plugin.remember(mock.get_nameid(), mock.get_attributes())
        self.request.response.redirect(getSite().absolute_url())
