# -*- coding: utf-8 -*-


from plone import api
from poi.pas.saml2.interfaces import DEFAULT_ID_USERS
from Products.Five import BrowserView
import six

class CurrentUserInspector(BrowserView):

    def __call__(self, *args, **kwargs):
        plugin = api.portal.get_tool('acl_users')[DEFAULT_ID_USERS]

        user = api.user.get_current()

        name = user.getUserName()
        id = user.getId()

        groups = api.group.get_groups(username = name)


        return str({
            "name": name,
            "id": id,
            "groups-from-api": [g.getGroupName() for g in groups],
            "groups-from-plugin": plugin.getGroupsForPrincipal(user)
        })


class PurgeUserData(BrowserView):

    def __call__(self, *args, **kwargs):
        plugin = api.portal.get_tool('acl_users')[DEFAULT_ID_USERS]

        old = plugin.purge_userdata()

        ret = {}

        for key, value in six.iteritems(old):
            ret[key] = value

        return ret