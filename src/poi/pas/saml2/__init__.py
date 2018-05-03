# -*- coding: utf-8 -*-
"""Init and utils."""
import os

from AccessControl.Permissions import add_user_folders
from Products.PluggableAuthService import registerMultiPlugin
from poi.pas.saml2.plugins import groups
from poi.pas.saml2.plugins import users
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('poi.pas.saml2')


def initialize(context):
    """Initializer called when used as a Zope 2 product.
    """
    registerMultiPlugin(users.PoiUsersPlugin.meta_type)
    context.registerClass(
        users.PoiUsersPlugin,
        permission=add_user_folders,
        icon=os.path.join(os.path.dirname(__file__), 'plugins', 'users.png'),
        constructors=(
            users.manage_addPoiUsersPluginForm,
            users.manage_addPoiUsersPlugin
        ),
        visibility=None
    )

    registerMultiPlugin(groups.PoiGroupsPlugin.meta_type)
    context.registerClass(
        groups.PoiGroupsPlugin,
        permission=add_user_folders,
        icon=os.path.join(os.path.dirname(__file__), 'plugins', 'groups.png'),
        constructors=(
            groups.manage_addPoiGroupsPluginForm,
            groups.manage_addPoiGroupsPlugin
        ),
        visibility=None
    )

