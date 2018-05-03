# -*- coding: utf-8 -*-

import base64
import re
from abc import ABCMeta, abstractmethod

import requests
from saml2 import samlp
from utils import xmlsec_path


class SettingsFactory(object):
    __metaclass__ = ABCMeta

    def prod_IdpSettings(self, request, xmlstr):
        idp_settings_prod = {
            "entityid": self.get_entityid(xmlstr),
            "name": "POI-PROD restrictied IdP",
            "service": {
                "idp": {
                    "endpoints": {
                        "single_sign_on_service": {
                            "url": self.endpoint_url(request),
                            "binding": None
                        },
                        "x509cert": self.x509cert(request)
                    }
                }
            },
            "xmlsec_binary": xmlsec_path(),
            "metadata": {
                "inline": [self.get_metadata(xmlstr)],
            },
            "attribute_map_dir": None,
            "only_use_keys_in_metadata": False,
            "allow_unknown_attributes": True,
        }
        return idp_settings_prod

    def get_metadata(self, xmlstr):
        response = samlp.response_from_string(xmlstr)

        issuer = response.issuer.text.replace('http://', 'https://')

        meta_url = issuer + '/metadata'
        xml_response = requests.get(meta_url, timeout=5)
        return xml_response.text

    def get_entityid(self, xmlstr):
        # Problem 1: wie es aussieht bekommen wir bei Prod PartnerNet als Audience
        # https://qa-autohaus.auto-partner.net/Dealer/saml2
        xml_audience = re.search('<saml2:Audience>(.+?)</saml2:Audience>', xmlstr)
        return xml_audience.group(1)

    def create_settings_dictionary(self, request):
        encoded_xmlstr = request.form['SAMLResponse']
        xmlstr = base64.decodestring(encoded_xmlstr)

        return self.prod_IdpSettings(request, xmlstr), xmlstr

    @abstractmethod
    def endpoint_url(self, request):
        pass

    @abstractmethod
    def x509cert(self, request):
        pass
