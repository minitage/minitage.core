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
import os
import sys
import shutil
import optparse
import ConfigParser

from minitage.core import interfaces

class test:pass
path = os.path.expanduser('~/iamauniquetestfileformatiwillberemoveafterthetest')
class testInterfaces(unittest.TestCase):

    def testFactory(self):
        config="""
[minibuild]
depends=python
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=invalid

[interface]
item1=minitage.core.tests.test_interfaces.test
"""
        open('%s' % path, 'w').write(config)
        try:
            interfaces.IFactory('not', path)
        except interfaces.InvalidConfigForFactoryError,e:
            self.assertTrue(isinstance(e, interfaces.InvalidConfigForFactoryError))

        i = interfaces.IFactory('interface', path)
        self.assertEquals(i.products['item1'].__name__, 'test')
        self.assertRaises(interfaces.InvalidComponentClassError, i.register, 'foo', 'foo.Bar')
        self.assertRaises(interfaces.NotImplementedMethodError, i.__call__, 'foo')

    def testProduct(self):
        p = interfaces.IProduct()
        self.assertRaises(interfaces.NotImplementedMethodError, p.match, 'foo')

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testInterfaces))
    unittest.TextTestRunner(verbosity=2).run(suite)

# vim:set et sts=4 ts=4 tw=80:
