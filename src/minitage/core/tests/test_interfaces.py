__docformat__ = 'restructuredtext en'
import unittest
import os
import sys
import shutil
import optparse
import ConfigParser

from minitage.core import interfaces

class test(object):
        """."""


from minitage.core.testing import LAYER
from minitage.core.tests import base


class testInterfaces(base.TestCase):
    """testInterfaces"""
    layer = LAYER

    def testFactory(self):
        """testFactory"""
        config = """
[minibuild]
dependencies=python
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=invalid

[minitage.interface]
item1=minitage.core.tests.test_interfaces:test
"""
        open('%s' % self.path, 'w').write(config)
        try:
            interfaces.IFactory('not', self.path)
        except interfaces.InvalidConfigForFactoryError,e:
            self.assertTrue(isinstance(e,
                                       interfaces.InvalidConfigForFactoryError))

        i = interfaces.IFactory('interface', self.path)
        self.assertEquals(i.products['item1'].__name__, 'test')
        self.assertRaises(interfaces.InvalidComponentClassError,
                          i.register, 'foo', 'foo.Bar')
        self.assertRaises(NotImplementedError, i.__call__, 'foo')

    def testProduct(self):
        """testProduct"""
        p = interfaces.IProduct()
        self.assertRaises(NotImplementedError, p.match, 'foo')

    def setUp(self):
        self.path = os.path.join(self.layer['p'], 'testinter')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testInterfaces))
    return suite

