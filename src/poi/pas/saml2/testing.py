# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.protect import auto
from plone.testing import Layer
from plone.testing import z2
from Products.CMFCore.interfaces import ISiteRoot
from Products.PlonePAS.setuphandlers import migrate_root_uf
from zope.component import provideUtility

import poi.pas.saml2


ORIGINAL_CSRF_DISABLED = auto.CSRF_DISABLED


class PoiPasSaml2ZopeLayer(Layer):

    defaultBases = (
        z2.INTEGRATION_TESTING,
    )

    # Products that will be installed, plus options
    products = (
        ('Products.GenericSetup', {'loadZCML': True, 'product': True}, ),
        ('Products.CMFCore', {'loadZCML': True, 'product': True}, ),
        ('Products.PluggableAuthService', {
            'loadZCML': True, 'product': True},),
        ('Products.PluginRegistry', {'loadZCML': True, 'product': True}, ),
        ('Products.PlonePAS', {'loadZCML': True, 'product': True}, ),
        ('plone.behavior', {'loadZCML': True, 'product': False}, ),
        ('poi.pas.saml2', {'loadZCML': True, 'product': False}, ),
    )

    def setUp(self):
        self.setUpZCML()

    def testSetUp(self):
        self.setUpProducts()
        provideUtility(self['app'], provides=ISiteRoot)
        migrate_root_uf(self['app'])

    def setUpZCML(self):
        """Stack a new global registry and load ZCML configuration of Plone
        and the core set of add-on products into it.
        """
        # Load dependent products's ZCML
        from zope.configuration import xmlconfig
        from zope.dottedname.resolve import resolve

        import z3c.autoinclude
        xmlconfig.file(
            'meta.zcml',
            z3c.autoinclude,
            context=self['configurationContext']
        )

        def loadAll(filename):
            for p, config in self.products:
                if not config['loadZCML']:
                    continue
                try:
                    package = resolve(p)
                except ImportError:
                    continue
                try:
                    xmlconfig.file(
                        filename,
                        package,
                        context=self['configurationContext']
                    )
                except IOError:
                    pass

        loadAll('meta.zcml')
        loadAll('configure.zcml')
        loadAll('overrides.zcml')

    def setUpProducts(self):
        """Install all old-style products listed in the the ``products`` tuple
        of this class.
        """
        for prd, config in self.products:
            if config['product']:
                z2.installProduct(self['app'], prd)


POIPASSAML2_ZOPE_FIXTURE = PoiPasSaml2ZopeLayer()


class PoiPasSaml2PloneLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        auto.CSRF_DISABLED = True
        self.loadZCML(package=poi.pas.saml2)
        z2.installProduct(app, 'poi.pas.saml2')

    def tearDownZope(self, app):
        auto.CSRF_DISABLED = ORIGINAL_CSRF_DISABLED

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'poi.pas.saml2:default')


POIPASSAML2_PLONE_FIXTURE = PoiPasSaml2PloneLayer()


POIPASSAML2_PLONE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(POIPASSAML2_PLONE_FIXTURE,),
    name='PoiPasSaml2PloneLayer:IntegrationTesting'
)


POIPASSAML2_PLONE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(POIPASSAML2_PLONE_FIXTURE,),
    name='PoiPasSaml2PloneLayer:FunctionalTesting'
)


POIPASSAML2_PLONE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        POIPASSAML2_PLONE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='PoiPasSaml2PloneLayer:AcceptanceTesting'
)
