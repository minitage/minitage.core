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
from minitage.core import interfaces, makers
from minitage.core.makers import buildout

class TestInterfaces(unittest.TestCase):
    """TestInterfaces"""

    def testIMaker(self):
        """testIMaker"""
        i = makers.interfaces.IMaker()
        self.assertRaises(interfaces.NotImplementedError,
                          i.make, 'foo', {'bar':'loo'})
        self.assertRaises(interfaces.NotImplementedError,
                          i.reinstall, 'foo', {'bar':'loo'})
        self.assertRaises(interfaces.NotImplementedError,
                          i.match, 'foo')

    def testFactory(self):
        """testFactory"""
        f = makers.interfaces.IMakerFactory()
        buildout = f('buildout')
        self.assertEquals(buildout.__class__.__name__,
                          makers.buildout.BuildoutMaker.__name__)
        self.assertEquals(buildout.__module__,
                          makers.buildout.BuildoutMaker\
                          .__module__.split('.').pop())

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInterfaces))
    unittest.TextTestRunner(verbosity=2).run(suite)

# vim:set et sts=4 ts=4 tw=80:
