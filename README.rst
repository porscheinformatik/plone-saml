.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

==============================================================================
poi.pas.saml2
==============================================================================

Provides Partner Net SAML2 users as Plone Users.

Features
--------

Group:

- provides behavior ``poipas.group`` to mark some content as a group
- provides pas plugin to expose the group marked content as a group

User:

- accept incoming SAML2 request
- start challenge request - response for saml request
- accept saml2 response
- remeber user and login in using authtkt
- expose saml2 attributes as propertysheet
- add user to group by a given saml2 property



Installation
------------

Install poi.pas.saml2 by adding it to your buildout::

    [buildout]

    ...

    eggs =
        poi.pas.saml2


and then running ``bin/buildout``


Support
-------

If you are having issues, please let us know.
Send an e-mail to support@kleinundpartner.at


License
-------

The project is licensed under the GPLv2.
