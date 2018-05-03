# -*- coding: utf-8 -*-
from Acquisition import aq_base
from plone.autoform.interfaces import IFormFieldProvider
from plone.indexer.decorator import indexer
from plone.supermodel import directives
from plone.supermodel import model
from zope import schema
from zope.interface import Interface
from zope.interface import provider


@provider(IFormFieldProvider)
class IGroup(model.Schema):
    """Expose this type as a group matching the SAML2 groups.
    """

    group_enabled = schema.Bool(
        title=u'Group enabled',
        description=u'Expose this type as a group to match SAML2 groups.',
        default=True,
        required=False,
    )
    directives.fieldset(
        'settings',
        fields=['group_enabled'],
    )


@indexer(Interface)
def group_enabled_indexer(obj, **kw):
    return aq_base(obj).group_enabled
