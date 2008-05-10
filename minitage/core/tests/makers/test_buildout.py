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

import os
import shutil
import unittest

from minitage.core import interfaces, makers, fetchers
from minitage.core.tests  import test_common



ocwd = os.getcwd()
path = os.path.expanduser('~/iamauniquetestdirformatiwillberemoveafterthetest')
ipath = os.path.expanduser(
    '~/iamauniquetestdirformatiwillberemoveafterthetest/test'
)
testopts = dict(path=path)
class TestBuildout(unittest.TestCase):
    """testBuildout"""

    def setUp(self):
        """."""
        os.chdir(ocwd)
        test_common.createMinitageEnv(path)
        os.mkdir(ipath)
        os.chdir(ipath)
        test_common.write('buildout.cfg', """
[makers]
[buildout]
options = -c buildout.cfg  -vvvvvv
parts = x
develop = .
[x]
recipe = toto """)
        test_common.write('setup.py', """
from setuptools import setup
setup(name='toto', entry_points={
'zc.buildout': ['default = toto:test']}) """)

        test_common.write('toto.py', """
class test:
    def __init__(self,a, b, c):
        pass

    def install(a):
        print "foo" """)
        test_common.bootstrap_buildout(ipath)

    def tearDown(self):
        """."""
        if os.path.isdir(path):
            shutil.rmtree(path)

    def testDelete(self):
        """testDelete"""
        p = '%s/%s' % (path, 'test2')
        if not os.path.isdir(p):
            os.mkdir(p)
        mf = makers.interfaces.IMakerFactory()
        b = mf('buildout')
        self.assertTrue(os.path.isdir(p))
        b.delete(p)
        self.assertFalse(os.path.isdir(p))

    def testInstall(self):
        """testInstall"""
        mf = makers.interfaces.IMakerFactory('buildout.cfg')
        buildout = mf('buildout')
        # must not die ;)
        buildout.make(ipath)
        self.assertTrue(True)

    def testReInstall(self):
        """testReInstall"""
        mf = makers.interfaces.IMakerFactory('buildout.cfg')
        buildout = mf('buildout')
        # must not die ;)
        buildout.make(ipath)
        buildout.reinstall(ipath)
        self.assertTrue(True)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBuildout))
    unittest.TextTestRunner(verbosity=2).run(suite)

# vim:set et sts=4 ts=4 tw=80:
