# -*- coding: utf-8 -*-
from poi.pas.saml2.interfaces import DEFAULT_ID_USERS
from poi.pas.saml2.interfaces import DEFAULT_ID_GROUPS
from poi.pas.saml2.plugins.groups import PoiGroupsPlugin
from poi.pas.saml2.plugins.users import PoiUsersPlugin
from Products.CMFPlone.interfaces import INonInstallable
from zope.component.hooks import getSite
from zope.interface import implementer

TITLE_USERS = 'Partner Net to Plone SAML2 plugin - Users (poi.pas.saml2)'
TITLE_GROUPS = 'Partner Net to Plone SAML2 plugin - Groups (poi.pas.saml2)'

@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return [
            'poi.pas.saml2:uninstall',
        ]


def _add_plugin(pas, pluginid, title, pluginclass):
    if pluginid in pas.objectIds():
        return title + ' already installed.'
    plugin = pluginclass(pluginid, title=title)
    if pluginid in pas.objectIds():
        return title + ' already installed.'
    pas._setObject(pluginid, plugin)
    plugin = pas[plugin.getId()]  # get plugin acquisition wrapped!
    for info in pas.plugins.listPluginTypeInfo():
        interface = info['interface']
        if not interface.providedBy(plugin):
            continue
        pas.plugins.activatePlugin(interface, plugin.getId())
        pas.plugins.movePluginsDown(
            interface,
            [x[0] for x in pas.plugins.listPlugins(interface)[:-1]],
        )


def _remove_plugin(pas, pluginid):
    if pluginid in pas.objectIds():
        pas.manage_delObjects([pluginid])


def post_install(context):
    """Post install script"""
    aclu = getSite().acl_users
    _add_plugin(aclu, DEFAULT_ID_USERS, TITLE_USERS, PoiUsersPlugin)
    _add_plugin(aclu, DEFAULT_ID_GROUPS, TITLE_GROUPS, PoiGroupsPlugin)


def uninstall(context):
    """Uninstall script"""
    aclu = getSite().acl_users
    _remove_plugin(aclu, DEFAULT_ID_USERS)
    _remove_plugin(aclu, DEFAULT_ID_GROUPS)
