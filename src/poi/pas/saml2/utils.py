# -*- coding: utf-8 -*-
from plone import api
from poi.pas.saml2.interfaces import _GROUP_ATTRIBUTE
from zope.component import getUtility
from interfaces import ISaml2RightsManager

import logging


logger = logging.getLogger(__name__)


def group_attribute():
    return _GROUP_ATTRIBUTE


def _id_with_postfix(baseid, postfix):
    if not postfix:
        return baseid
    return baseid + '_-_' + postfix


def _make_record(brain, postfix=''):
    title = brain.Title or brain.getId
    if postfix:
        title += '({0})'.format(postfix)
    return {
        'id': _id_with_postfix(brain.getId, postfix),
        'title': title,
        'description': brain.description or '',
        'email': '',
    }


def _groups_brains():
    catalog = api.portal.get_tool('portal_catalog')
    # no dups!
    found = set()
    for brain in catalog.unrestrictedSearchResults(group_enabled=True):
        if brain.getId in found:
            logger.warn(
                'Group with ID {0} found at least twice!'.format(
                    brain.getId,
                )
            )
            continue
        found.update(brain.getId)
        yield brain

def group_ids(plugin):
    result = []
    manager = get_saml2rightsManager()
    for brain in _groups_brains():
        group_names = manager.groups_for_brain(brain)

        if group_names:
            result.extend(group_names)

    return result


def group_infos(plugin):
    result = []
    for brain in _groups_brains():
        if brain.portal_type == 'Cardealer':
            result.append(_make_record(brain))
            result.append(_make_record(brain, postfix='jobs'))
        elif brain.portal_type == 'Country':
            result.append(_make_record(brain, postfix='manager'))
    return result


def group_info(plugin, group_id):

    if not group_id:
        return None

    catalog = api.portal.get_tool('portal_catalog')
    splitted = group_id.split('_-_')
    postfix = ''
    if len(splitted) > 1:
        postfix = splitted[1]
    brains = catalog(group_enabled=True, getId=splitted[0])
    if len(brains) > 1:
        logger.warn(
            'Group with ID {0} found {1} times. Took first.'.format(
                group_id,
                len(brains)
            )
        )
    if len(brains) > 0:
        brain = brains[0]
        return _make_record(brain, postfix)
    return None

def get_saml2rightsManager():
    return getUtility(ISaml2RightsManager)
