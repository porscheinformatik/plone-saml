# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from abc import ABCMeta, abstractmethod
import six


DEFAULT_ID_USERS = 'poisaml2users'
DEFAULT_ID_GROUPS = 'poisaml2groups'
_GROUP_ATTRIBUTE = 'group'

# this "role" is a hack so user plugins can add the user to groups that are not based on some SAML2
# roles
SAML2_DEFAULT_ROLE = "saml2_default_role"

class IPoiUsersPlugin(Interface):
    """Plugin to connect Partner Net SAML2 to Plone - Users"""

    def remember(result):
        """remember user as valid

        result is saml user data.
        """

class IPoiGroupsPlugin(Interface):
    """Plugin to connect Partner Net SAML2 to Plone - Groups"""

class IPoiPasSaml2Layer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""

class ISaml2RightsManager(Interface):
    """utility marker interface"""

class AbstractSaml2RightsManager(six.with_metaclass(ABCMeta, object)):
    @abstractmethod
    def redirection_url(self, context, saml_data):
        pass


    # samlrole2group / auch users.py
    @abstractmethod
    def samlrole2groups(self, role, portal, userdata):
        pass


    # group-info?

    @abstractmethod
    def groups_for_brain(self, brain):
        """
        Receives a brain of a group object and returns all group names for that object.

        A "group object" is defined by providing
        :param brain:
        :return:
        """
        pass


    @abstractmethod
    def create_settings_dictionary(self, request):
        """
        Creates a dictionary of saml2 configs to be used within a saml2.config.Config object.

        :param request: the saml2 authentication request
        :return: a tuple of the dictionary in question as well as the raw xml-String that was
        retrieved from the request
        """
        pass

    def generally_allowed_groups(self, request):
        """
        Returns all names of groups that are not managed by the saml2plugin that are generally
        allowed for users.

        Defaults to [u'Site Administrators', u'Administrators'].
        Overwrite in your Saml2RightsManager as needed.

        :param request: the current reques
        :return: a list of group names
        """
        return [u'Site Administrators', u'Administrators']