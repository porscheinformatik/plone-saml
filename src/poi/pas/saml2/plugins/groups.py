# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from operator import itemgetter
from poi.pas.saml2 import utils
from poi.pas.saml2.interfaces import IPoiGroupsPlugin
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PlonePAS import interfaces as plonepas_interfaces
from Products.PlonePAS.plugins.group import PloneGroup
from Products.PluggableAuthService.interfaces import plugins as pas_interfaces
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.UserPropertySheet import UserPropertySheet
from zope.interface import implementer

import logging
import os


logger = logging.getLogger(__name__)
tpl_dir = os.path.join(os.path.dirname(__file__), 'browser')

_marker = {}


def manage_addPoiGroupsPlugin(context, id, title='', RESPONSE=None, **kw):
    """Create an instance of a PoiSaml2 Plugin.
    """
    plugin = PoiGroupsPlugin(id, title, **kw)
    context._setObject(plugin.getId(), plugin)
    if RESPONSE is not None:
        RESPONSE.redirect('manage_workspace')


manage_addPoiGroupsPluginForm = PageTemplateFile(
    os.path.join(tpl_dir, 'add_plugin.pt'),
    globals(),
    __name__='addPoiGroupsPlugin'
)


@implementer(
    IPoiGroupsPlugin,
    pas_interfaces.IGroupEnumerationPlugin,
    pas_interfaces.IPropertiesPlugin,
    plonepas_interfaces.capabilities.IGroupCapability,
    plonepas_interfaces.group.IGroupIntrospection,
)
class PoiGroupsPlugin(BasePlugin):
    """PoiSaml2 PAS Plugin
    """
    security = ClassSecurityInfo()
    meta_type = 'PoiSaml2 Groups Plugin'
    BasePlugin.manage_options

    # Tell PAS not to swallow our exceptions
    _dont_swallow_my_exceptions = True

    def __init__(self, id, title=None, **kw):
        self._setId(id)
        self.title = title
        self.plugin_caching = True

    # specific helpers

    def _get_propertysheet_of_info(self, info):
        if info is None:
            return None
        sheet = UserPropertySheet(
            self.getId(),
            title=info['title'],
            description=info['description'],
            email=info['email']
        )
        return sheet

    def _get_group_by_info(self, info):
        if info is None:
            return None
        group = PloneGroup(info['id'], info['id']).__of__(self)
        pas = self._getPAS()
        plugins = pas.plugins

        # add properties
        # 1.) shortcut to own properties
        data = self._get_propertysheet_of_info(info)
        group.addPropertysheet(self.getId(), data)

        properties_provider = plugins.listPlugins(
            pas_interfaces.IPropertiesPlugin
        )

        # 2.) other possible plugins
        for propfinder_id, propfinder in properties_provider:
            if propfinder_id == self.getId():
                continue
            data = propfinder.getPropertiesForUser(group, None)
            if not data:
                continue
            group.addPropertysheet(propfinder_id, data)

        # add subgroups
        group._addGroups(
            pas._getGroupsForPrincipal(
                group,
                None,
                plugins=plugins
            )
        )
        # add roles
        role_provider = plugins.listPlugins(pas_interfaces.IRolesPlugin)
        for rolemaker_id, rolemaker in role_provider:
            roles = rolemaker.getRolesForPrincipal(group, None)
            if not roles:
                continue
            group._addRoles(roles)
        return group

    # ##
    # plonepas_interfaces.capabilities.IGroupCapability
    # (plone ui specific)
    #
    @security.public
    def allowGroupAdd(self, principal_id, group_id):
        """
        True if this plugin will allow adding a certain principal to
        a certain group.
        """
        return False

    @security.public
    def allowGroupRemove(self, principal_id, group_id):
        """
        True if this plugin will allow removing a certain principal
        from a certain group.
        """
        return False

    # ##
    # plonepas_interfaces.capabilities.IGroupIntrospection
    # (plone ui specific)

    def getGroupById(self, group_id):
        """
        Returns the portal_groupdata-ish object for a group
        corresponding to this id. None if group does not exist here!
        """
        return self._get_group_by_info(utils.group_info(self, group_id))

    def getGroups(self):
        """
        Returns an iteration of the available groups
        """
        result = []
        for info in utils.group_infos(self):
            result.append(self._get_group_by_info(info))
        return result

    def getGroupIds(self):
        """
        Returns a list of the available groups (ids)
        """
        return list(sorted(utils.group_ids(self)))

    def getGroupMembers(self, group_id):
        """
        returns the members of the given group as tuple
        """
        result = ()
        # Not implemented due to difficulty to get all members of a groups
        # since data is in saml and plone only knows about users logged in at
        # a certain time. data could be outdated.
        return result

    # ##
    # pas_interfaces.plugins.IPropertiesPlugin

    def getPropertiesForUser(self, group, request=None):
        group_id = group.getId()
        ret = self._get_propertysheet_of_info(
            utils.group_info(self, group_id)
        )
        return ret

    # ##
    # pas_interfaces.IGroupEnumerationPlugin
    #
    #  Allow querying groups by ID, and searching for groups.
    #
    @security.private
    def enumerateGroups(
        self,
        id=None,
        exact_match=False,
        sort_by=None,
        max_results=None,
        **kw
    ):
        """ -> ( group_info_1, ... group_info_N )

        o Return mappings for groups matching the given criteria.

        o 'id' in combination with 'exact_match' true, will
          return at most one mapping per supplied ID ('id' and 'login'
          may be sequences).

        o If 'exact_match' is False, then 'id' may be treated by
          the plugin as "contains" searches (more complicated searches
          may be supported by some plugins using other keyword arguments).

        o If 'sort_by' is passed, the results will be sorted accordingly.
          known valid values are 'id' (some plugins may support others).

        o If 'max_results' is specified, it must be a positive integer,
          limiting the number of returned mappings.  If unspecified, the
          plugin should return mappings for all groups satisfying the
          criteria.

        o Minimal keys in the returned mappings:

          'id' -- (required) the group ID

          'pluginid' -- (required) the plugin ID (as returned by getId())

          'properties_url' -- (optional) the URL to a page for updating the
                              group's properties.

          'members_url' -- (optional) the URL to a page for updating the
                           principals who belong to the group.

        o Plugin *must* ignore unknown criteria.

        o Plugin may raise ValueError for invalid critera.

        o Insufficiently-specified criteria may have catastrophic
          scaling issues for some implementations.
        """
        if id:
            kw['id'] = id
        result = []
        for gid in utils.group_ids(self):
            record = {
                'id': gid,
                'pluginid': self.getId(),
            }
            if not kw:  # show all
                result.append(record)
                continue
            if 'id' in kw:
                if exact_match:
                    if 'id' in kw and kw['id'] == gid:
                        result.append(record)
                    continue
                if gid.startswith(kw['id']):
                    result.append(record)
                    continue
        if sort_by and 'id' in sort_by:
            result = sorted(result, key=itemgetter('id'))
        if max_results and len(result) >= max_results:
            result = result[:max_results]

        return result

InitializeClass(PoiGroupsPlugin)
