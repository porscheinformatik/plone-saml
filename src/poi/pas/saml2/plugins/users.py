# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from BTrees.OOBTree import OOBTree
from operator import itemgetter
from persistent.dict import PersistentDict
from plone import api
from Products.CMFPlone.utils import safe_unicode
from poi.pas.saml2 import utils
from poi.pas.saml2.interfaces import IPoiUsersPlugin
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.interfaces import plugins as pas_interfaces
from Products.PluggableAuthService.interfaces.authservice import _noroles
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.UserPropertySheet import UserPropertySheet
from zope.interface import implementer
from poi.pas.saml2.utils import get_saml2rightsManager

import logging
import os
import uuid
import pdb
from poi.pas.saml2.interfaces import _GROUP_ATTRIBUTE


logger = logging.getLogger(__name__)
tpl_dir = os.path.join(os.path.dirname(__file__), 'browser')

_marker = {}


def manage_addPoiUsersPlugin(context, id, title='', RESPONSE=None, **kw):
    """Create an instance of a PoiSaml2 Plugin.
    """
    plugin = PoiUsersPlugin(id, title, **kw)
    context._setObject(plugin.getId(), plugin)
    if RESPONSE is not None:
        RESPONSE.redirect('manage_workspace')


manage_addPoiUsersPluginForm = PageTemplateFile(
    'users_add_plugin.pt',
    globals(),
    __name__='addPoiUsersPlugin'
)


@implementer(
    IPoiUsersPlugin,
    pas_interfaces.IAuthenticationPlugin,
    pas_interfaces.IPropertiesPlugin,
    pas_interfaces.IUserEnumerationPlugin,
    pas_interfaces.IGroupsPlugin,
)
class PoiUsersPlugin(BasePlugin):
    """PoiSaml2 PAS Plugin
    """
    security = ClassSecurityInfo()
    meta_type = 'PoiSaml2 Users Plugin'
    BasePlugin.manage_options

    # Tell PAS not to swallow our exceptions
    _dont_swallow_my_exceptions = True

    def __init__(self, id, title=None, **kw):
        self._setId(id)
        self.title = title
        self.plugin_caching = True
        self._init_trees()

    def _init_trees(self):
        # userid -> userdata
        self._userdata_by_userid = OOBTree()

    def _check_password(self, identity, password):
        return password == identity['secret']

    def _propertysheet(self, userid, identity):
        pdata = {
            'fullname': (
                identity['Person.FirstName'][0] +
                ' ' +
                identity['Person.LastName'][0]
            ),
            'email': identity['Person.Email'][0]
        }
        return UserPropertySheet(userid, **pdata)

    @security.private
    def remember_identity(self, userid, userdata):
        """stores poisaml2 result data
        """
        # first create an identity for this time of login
        portal = api.portal.get()
        manager = get_saml2rightsManager()

        identity = PersistentDict(
            userid=userid,
            secret=str(uuid.uuid4()),
        )
        identity.update(userdata)
        logger.info(userdata)
        identity[_GROUP_ATTRIBUTE] = set()
        logger.info('add groups to user:')
        #for samlrole in userdata['Person.Roles']:
        #    if samlrole in SAMLROLE_TO_GROUP:
        for samlrole in userdata['Person.Roles']:
            groups = manager.samlrole2groups(samlrole, portal, userdata)
            if groups:
                identity[_GROUP_ATTRIBUTE].update(groups)
                logger.info("{} -> {}".format(samlrole, groups))

        self._userdata_by_userid[userid] = identity
        return identity

    @security.private
    def remember(self, userid, userdata):
        """remember user as valid

        result is poisaml2 result data.
        """
        # lookup user by passed saml2 data
        identity = self.remember_identity(userid, userdata)

        # login: get new security manager
        aclu = api.portal.get_tool('acl_users')
        user = aclu._findUser(aclu.plugins, userid)
        accessed, container, name, value = aclu._getObjectContext(
            self.REQUEST['PUBLISHED'],
            self.REQUEST
        )
        user = aclu._authorizeUser(
            user,
            accessed,
            container,
            name,
            value,
            _noroles
        )

        # do login post-processing
        self.REQUEST['__ac_password'] = identity['secret']
        mt = api.portal.get_tool('portal_membership')
        mt.loginUser(self.REQUEST)

    # ##
    # pas_interfaces.IAuthenticationPlugin

    @security.public
    def authenticateCredentials(self, credentials):
        """ credentials -> (userid, login)

        - 'credentials' will be a mapping, as returned by IExtractionPlugin.
        - Return a  tuple consisting of user ID (which may be different
          from the login name) and login
        - If the credentials cannot be authenticated, return None.
        """
        login = credentials.get('login', None)
        password = credentials.get('password', None)
        if not login or login not in self._userdata_by_userid:
            return None
        identity = self._userdata_by_userid[login]
        if self._check_password(identity, password):
            return login, login

    # ##
    # pas_interfaces.plugins.IPropertiesPlugin

    @security.private
    def getPropertiesForUser(self, user, request=None):
        identity = self._userdata_by_userid.get(
            user.getId(),
            _marker
        )
        if identity is _marker:
            return None

        ret = self._propertysheet(user, identity)
        return ret
    # ##
    # pas_interfaces.plugins.IUserEnumaration

    @security.private
    def enumerateUsers(self, id=None, login=None, exact_match=False,
                       sort_by=None, max_results=None, **kw):
        """-> ( user_info_1, ... user_info_N )

        o Return mappings for users matching the given criteria.

        o 'id' or 'login', in combination with 'exact_match' true, will
          return at most one mapping per supplied ID ('id' and 'login'
          may be sequences).

        o If 'exact_match' is False, then 'id' and / or login may be
          treated by the plugin as "contains" searches (more complicated
          searches may be supported by some plugins using other keyword
          arguments).

        o If 'sort_by' is passed, the results will be sorted accordingly.
          known valid values are 'id' and 'login' (some plugins may support
          others).

        o If 'max_results' is specified, it must be a positive integer,
          limiting the number of returned mappings.  If unspecified, the
          plugin should return mappings for all users satisfying the criteria.

        o Minimal keys in the returned mappings:

          'id' -- (required) the user ID, which may be different than
                  the login name

          'login' -- (required) the login name

          'pluginid' -- (required) the plugin ID (as returned by getId())

          'editurl' -- (optional) the URL to a page for updating the
                       mapping's user

        o Plugin *must* ignore unknown criteria.

        o Plugin may raise ValueError for invalid criteria.

        o Insufficiently-specified criteria may have catastrophic
          scaling issues for some implementations.
        """

        if id and login and id != login:
            raise ValueError('plugin does not support id different from login')
        search_id = id or login
        # if search_id is None: return tuple()
        pluginid = self.getId()

        ret = list()
        # shortcut for exact match of login/id
        identity = None
        if (
            exact_match and
            search_id and
            search_id in self._userdata_by_userid
        ):
            identity = self._userdata_by_userid[search_id]
            ret.append({
                'id': identity['userid'].decode('utf8'),
                'login': identity['userid'],
                'pluginid': pluginid
            })
            return ret

        # non exact expensive search
        special_search = None
        if search_id and search_id.startswith('#'):
            special_search = safe_unicode(search_id[1:])
        for userid in self._userdata_by_userid:
            if userid:
                if search_id and not userid.startswith(search_id) \
                and special_search is None:
                    continue
                identity = self._userdata_by_userid[userid]
                if special_search is not None:
                    if not identity['Person.LastName'][0].startswith(special_search) \
                    and not identity['Person.FirstName'][0].startswith(special_search):
                        continue
                ret.append({
                    'id': identity['userid'].decode('utf8'),
                    'login': identity['userid'],
                    'pluginid': pluginid
                })
                if max_results and len(ret) >= max_results:
                    break
        if sort_by in ['id', 'login']:
            return sorted(ret, key=itemgetter(sort_by))
        return ret

    # ##
    # pas_interfaces.IGroupsPlugin
    #
    #  Determine the groups to which a user belongs.

    @security.private
    def getGroupsForPrincipal(self, principal, request=None):
        """principal -> ( group_1, ... group_N )

        o Return a sequence of group names to which the principal
          (either a user or another group) belongs.

        o May assign groups based on values in the REQUEST object, if present
        """
        identity = self._userdata_by_userid.get(principal.getId(), None)
        if identity is None:
            return ()
        groupnames = identity.get(utils.group_attribute(), None)
        if groupnames is None:
            return ()
        existing_groups = set(utils.group_ids(self))

        # TODO move this hardcoded group to rights administration plugin (v0.3)
        existing_groups.update([u'Site Administrators', u'Administrators'])
        valid_groups = existing_groups & set(groupnames)
        return tuple(sorted(valid_groups))

InitializeClass(PoiUsersPlugin)
