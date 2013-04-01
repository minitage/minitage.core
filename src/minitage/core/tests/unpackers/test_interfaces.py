__docformat__ = 'restructuredtext en'

import unittest
import os
from minitage.core import interfaces, unpackers
from minitage.core.unpackers import tar as mtar

from minitage.core.tests import base

class testInterfaces(base.TestCase):
    """testInterfaces"""

    def testIUnpacker(self):
        """testIUnpacker"""
        i = unpackers.interfaces.IUnpacker('ls', 'ls')
        self.assertRaises(NotImplementedError,
                          i.unpack, 'foo', 'bar')
        self.assertRaises(NotImplementedError,
                          i.match, 'foo')

    def testInit(self):
        """testInit"""
        f = unpackers.interfaces.IUnpacker('ls', 'ls')
        self.assertEquals(f.name,'ls')
        f = unpackers.interfaces.IUnpacker('ls','/bin/ls')

    def testFactory(self):
        """testFactory"""
        f = unpackers.interfaces.IUnpackerFactory()
        os.system('touch toto;tar cvf tar toto')
        tar = f('tar')
        self.assertEquals(tar.__class__.__name__,
                          unpackers.tar.TarUnpacker.__name__)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testInterfaces))
    return suite

# vim:set et sts=4 ts=4 tw=80:
