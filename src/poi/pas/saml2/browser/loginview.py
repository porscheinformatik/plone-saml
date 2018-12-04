# -*- coding: utf-8 -*-
#####
###  Login from PartnerNet (Country and dealer)
###
#####
# from poi.utils.poi_tools.searchtools import poi_get_alldealer
# from poi.utils.poi_tools.get_serverconfig import get_servermode
import logging
from plone import api

from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from poi.pas.saml2.interfaces import DEFAULT_ID_USERS
from poi.pas.saml2.utils import get_saml2rightsManager
from saml2.client import Saml2Client
from saml2.config import Config as Saml2Config
from saml2.response import StatusResponse

logger = logging.getLogger(__name__)

# -------------------------------------------------
# Ohne asynchop=False geht es nicht.
# -------------------------------------------------
orig_call_init = StatusResponse.__init__


def patch__init__(self, sec_context, return_addrs=None, timeslack=0,
                  request_id=0, asynchop=True, conv_info=None):
    return orig_call_init(self, sec_context, return_addrs=None, timeslack=0,
                          request_id=0, asynchop=False, conv_info=None)


StatusResponse.__init__ = patch__init__


# -------------------------------------------------
# LOGIN Dealer ()
# -------------------------------------------------
class DealerLoginView(BrowserView):
    def __init__(self, *args, **kwargs):
        super(DealerLoginView, self).__init__(*args, **kwargs)
        self.saml2rights_manager = get_saml2rightsManager()

    def _saml(self):

        settings_dict, xmlstr = self.saml2rights_manager.create_settings_dictionary(self.request)

        spConfig = Saml2Config()
        spConfig.load(settings_dict)
        cli = Saml2Client(config=spConfig)
        try:
            binding = None
            poi_authn_response = cli.parse_authn_request_response(
                xmlstr, binding)
            poi_authn_response.get_identity()
            user_info = poi_authn_response.get_subject()
            username = user_info.text
        except Exception as e:
            logging.error(e)
            return {
                'exception': str(e),
                'httpcode': 401,
                'error': True,
            }

        return {
            'error': False,
            'ava': poi_authn_response.ava,
            'username': username,
            'PartnerNummer': str(
                poi_authn_response.ava["PartnerKey.PartnerNumber"][0]
            ),
            'PartnerUser': safe_unicode(
                poi_authn_response.ava["Person.LastName"][0]
            ),
            'UserCountry': poi_authn_response.ava["Portal.ID"][0],
        }

    @property
    def process(self):

        saml = self._saml()
        if saml['error']:
            logger.error(saml['exception'])

        logger.info("LOGIN: %s to %s" % (saml['PartnerNummer'], saml['PartnerUser']))

        # -------------------------------------------------
        # Login User and redirect to specific Folder
        # -------------------------------------------------
        plugin = api.portal.get_tool('acl_users')[DEFAULT_ID_USERS]
        plugin.remember(saml['username'], saml['ava'])

        redirkey = self.saml2rights_manager.redirection_url(self.context, saml)
        self.request.response.redirect(redirkey)

        # -------------------------------------------------
        # PROBLEM MIT PARTNERNET
        # -------------------------------------------------


# -------------------------------------------------
# LOGIN Country ()
# -------------------------------------------------
class LoginView(DealerLoginView):
    def __call__(self):
        saml = self._saml()
        if saml['error']:
            logger.error(saml['exception'])

        logger.info("LOGIN: %s to %s" % (saml['PartnerNummer'], saml['PartnerUser']))
        # -------------------------------------------------
        # Login User and redirect to specific Folder
        # -------------------------------------------------
        plugin = api.portal.get_tool('acl_users')[DEFAULT_ID_USERS]
        plugin.remember(saml['username'], saml['ava'])

        redirkey = self.saml2rights_manager.redirection_url(self.context, saml)
        self.request.response.redirect(redirkey)
