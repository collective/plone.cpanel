import os
import unittest
import robotsuite
from plone.testing import layered
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.helpers import PloneSandboxLayer
from zope.configuration import xmlconfig
from plone.testing import z2
from OFS.Application import AppInitializer

from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_ROBOT_TESTING, \
    ProductsCMFPloneLayer
import plone.cpanel

class PloneCPanelLayer(PloneSandboxLayer):
    # def getOne(self):
    #     app = getApp()
    #     return

    def setUpZope(self, app, configurationContext):

        import Products.CMFPlone
        xmlconfig.file(
            'configure.zcml',
            Products.CMFPlone,
            context=configurationContext
        )
        i = AppInitializer(app)
        i.install_virtual_hosting()
        z2.installProduct(app, 'Products.PageTemplates')
        i.install_standards()
        xmlconfig.file(
            'overrides.zcml',
            plone.cpanel,
            context=configurationContext
        )

    # def setUpPloneSite(self, portal):
    #     pass
    #
    # def tearDownPloneSite(self, portal):
    #     pass

PLONE_CPANEL_FIXTURE = PloneCPanelLayer()

CPANEL_TESTING = FunctionalTesting(
    bases=(PLONE_CPANEL_FIXTURE,
           PRODUCTS_CMFPLONE_ROBOT_TESTING,
           z2.ZSERVER_FIXTURE),
    name="CPanel:Acceptance"
)

def test_suite():
    suite = unittest.TestSuite()
    current_dir = os.path.abspath(os.path.dirname(__file__))
    robot_dir = os.path.join(current_dir, 'robot')
    robot_tests = [
        os.path.join('robot', doc) for doc in os.listdir(robot_dir)
        if doc.endswith('.robot') and doc.startswith('test_')
    ]
    for test in robot_tests:
        suite.addTests([
            layered(
                robotsuite.RobotTestSuite(test),
                layer=PRODUCTS_CMFPLONE_ROBOT_TESTING
            ),
        ])
    return suite
