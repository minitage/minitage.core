__docformat__ = 'restructuredtext en'

import unittest
from minitage.core import  makers
from minitage.core.tests import base

class TestInterfaces(base.TestCase):
    """TestInterfaces"""

    def testIMaker(self):
        """testIMaker"""
        i = makers.interfaces.IMaker()
        self.assertRaises(NotImplementedError,
                          i.install, 'foo', {'bar':'loo'})
        self.assertRaises(NotImplementedError,
                          i.reinstall, 'foo', {'bar':'loo'})
        self.assertRaises(NotImplementedError,
                          i.match, 'foo')
        self.assertRaises(NotImplementedError,
                          i.get_options, 'foo', 'foo')

    def testFactory(self):
        """testFactory"""
        f = makers.interfaces.IMakerFactory()
        buildout = f('buildout')
        self.assertEquals(buildout.__class__.__name__,
                          makers.buildout.BuildoutMaker.__name__)
        self.assertEquals(buildout.__module__,
                          makers.buildout.BuildoutMaker\
                          .__module__)
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInterfaces))
    return suite

# vim:set et sts=4 ts=4 tw=80:
