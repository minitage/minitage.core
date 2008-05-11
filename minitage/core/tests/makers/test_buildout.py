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

import sys
import os
import shutil
import unittest

from minitage.core import interfaces, makers, fetchers
from minitage.core.tests  import test_common
from minitage.core import api
from minitage.core import cli



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
        test_common.make_dummy_buildoutdir(ipath)

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
        buildout.install(ipath)
        self.assertTrue(True)

    def testInstallPart(self):
        """testInstall"""
        mf = makers.interfaces.IMakerFactory('buildout.cfg')
        buildout = mf('buildout')
        # must not die ;)
        buildout.install(ipath, {'parts': 'y'})
        self.assertEquals(open('%s/testbar' % ipath,'r').read(), 'foo')
        os.remove('%s/testbar' % ipath)


    def testInstallMultiPartStr(self):
        """testInstallMultiPartStr"""
        mf = makers.interfaces.IMakerFactory('buildout.cfg')
        buildout = mf('buildout')
        buildout.install(ipath, {'parts': ['y', 'z']})
        buildout.install(ipath, {'parts': 'y z'})
        self.assertEquals(open('%s/testbar' % ipath,'r').read(), 'foo')
        self.assertEquals(open('%s/testres' % ipath,'r').read(), 'bar')
        os.remove('%s/testbar' % ipath)
        os.remove('%s/testres' % ipath)


    def testInstallMultiPartList(self):
        """testInstallMultiPartList"""
        mf = makers.interfaces.IMakerFactory('buildout.cfg')
        buildout = mf('buildout')
        buildout.install(ipath, {'parts': ['y', 'z']})
        self.assertEquals(open('%s/testbar' % ipath,'r').read(), 'foo')
        self.assertEquals(open('%s/testres' % ipath,'r').read(), 'bar')
        os.remove('%s/testbar' % ipath)
        os.remove('%s/testres' % ipath)

    def testReInstall(self):
        """testReInstall"""
        mf = makers.interfaces.IMakerFactory('buildout.cfg')
        buildout = mf('buildout')
        # must not die ;)
        buildout.install(ipath)
        buildout.reinstall(ipath)
        self.assertTrue(True)

    def testGetOptions(self):
        """testGetOptions."""
        sys.argv = [sys.argv[0], '--config',
                    '%s/etc/minimerge.cfg' % path, 'minibuild-0']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        minibuild = api.Minibuild('a/minibuild')
        minibuild.category = 'eggs'
        minibuild.name = 'toto'
        mf = makers.interfaces.IMakerFactory('buildout.cfg')
        buildout = mf('buildout')
        pyvers = {'python_versions': ['2.4', '2.5']}
        options = buildout.get_options(minimerge, minibuild, **pyvers)
        self.assertEquals(options['parts'],
                          ['site-packages-2.4', 'site-packages-2.5'])
        minibuild.category = 'dependencies'
        options = buildout.get_options(minimerge, minibuild, **pyvers)
        minibuild.category = 'zope'
        options = buildout.get_options(minimerge, minibuild, **pyvers)
        self.assertFalse('parts' in options)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBuildout))
    unittest.TextTestRunner(verbosity=2).run(suite)

# vim:set et sts=4 ts=4 tw=80:
