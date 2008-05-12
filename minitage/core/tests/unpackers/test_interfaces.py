#!/usr/bin/env python

# Copyright (C) 2008, Mathieu PASQUET <kiorky@cryptelium.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

__docformat__ = 'restructuredtext en'

import unittest
from minitage.core import interfaces, unpackers
from minitage.core.unpackers import tar

class testInterfaces(unittest.TestCase):
    """testInterfaces"""

    def testIUnpacker(self):
        """testIUnpacker"""
        i = unpackers.interfaces.IUnpacker('ls', 'ls')
        self.assertRaises(interfaces.NotImplementedError,
                          i.unpack, 'foo', 'bar')
        self.assertRaises(interfaces.NotImplementedError,
                          i.match, 'foo')

    def testInit(self):
        """testInit"""
        f = unpackers.interfaces.IUnpacker('ls', 'ls')
        self.assertEquals(f.name,'ls')
        self.assertEquals(f.executable,'/bin/ls')
        f = unpackers.interfaces.IUnpacker('ls','/bin/ls')
        self.assertEquals(f.executable,'/bin/ls')
        self.assertRaises(unpackers.interfaces.UnpackerNotInPathError,
                        unpackers.interfaces.IUnpacker, 'ls','/bin/notfoundheh')

    def testFactory(self):
        """testFactory"""
        f = unpackers.interfaces.IUnpackerFactory()
        tar = f('tar')
        self.assertEquals(tar.__class__.__name__,
                          unpackers.tar.TarUnpacker.__name__)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testInterfaces))
    unittest.TextTestRunner(verbosity=2).run(suite)

# vim:set et sts=4 ts=4 tw=80:
