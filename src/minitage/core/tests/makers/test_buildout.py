__docformat__ = 'restructuredtext en'

import sys
import os
import shutil
import unittest
import tempfile

from minitage.core import interfaces, makers, fetchers
from minitage.core import api
from minitage.core import cli

from minitage.core.tests import base
from minitage.core.testing import make_dummy_buildoutdir


class TestBuildout(base.TestCase):
    """testBuildout"""

    def setUp(self):
        """."""
        self.path = self.layer['p']
        self.ipath =  self.layer['p'] +'/test/testbuildout'
        self.config=os.path.join(self.path,'etc','minimerge.cfg')
        make_dummy_buildoutdir(self.ipath)

    def tearDown(self):
        """."""
        if os.path.exists(self.ipath):
            shutil.rmtree(self.ipath)

    def testDelete(self):
        """testDelete"""
        p = '%s/%s' % (self.path, 'test2')
        if not os.path.isdir(p):
            os.mkdir(p)
        mf = makers.interfaces.IMakerFactory()
        b = mf('buildout')
        self.assertTrue(os.path.isdir(p))
        b.delete(p)
        self.assertFalse(os.path.isdir(p))

    def testBInstall(self):
        """testInstall"""
        mf = makers.interfaces.IMakerFactory(self.config)
        buildout = mf('buildout')
        # must not die ;)
        buildout.install(self.ipath, {"offline":True})
        self.assertTrue(True)

    def testInstallPart(self):
        """testInstall"""
        mf = makers.interfaces.IMakerFactory(self.config)
        buildout = mf('buildout')
        # must not die ;)
        buildout.install(self.ipath, {'offline':True,'parts': 'y'})
        self.assertEquals(open('%s/testbar' % self.ipath,'r').read(), 'foo')
        os.remove('%s/testbar' % self.ipath)


    def testInstallMultiPartStr(self):
        """testInstallMultiPartStr"""
        mf = makers.interfaces.IMakerFactory(self.config)
        buildout = mf('buildout')
        buildout.install(self.ipath, {"offline":True, 'parts': ['y', 'z']})
        buildout.install(self.ipath, {"offline":True, 'parts': 'y z'})
        self.assertEquals(open('%s/testbar' % self.ipath,'r').read(), 'foo')
        self.assertEquals(open('%s/testres' % self.ipath,'r').read(), 'bar')
        os.remove('%s/testbar' % self.ipath)
        os.remove('%s/testres' % self.ipath)


    def testInstallMultiPartList(self):
        """testInstallMultiPartList"""
        mf = makers.interfaces.IMakerFactory(self.config)
        buildout = mf('buildout')
        buildout.install(self.ipath, {"offline":True, 'parts': ['y', 'z']})
        self.assertEquals(open('%s/testbar' % self.ipath,'r').read(), 'foo')
        self.assertEquals(open('%s/testres' % self.ipath,'r').read(), 'bar')
        os.remove('%s/testbar' % self.ipath)
        os.remove('%s/testres' % self.ipath)

    def testReInstall(self):
        """testReInstall"""
        mf = makers.interfaces.IMakerFactory(self.config)
        buildout = mf('buildout')
        # must not die ;)
        buildout.install(self.ipath, {"offline":True})
        buildout.reinstall(self.ipath,{"offline":True})
        self.assertTrue(True)

    def testBGetOptions(self):
        """testGetOptions."""
        minimerge = self.fminimerge([sys.argv[0], '--config',
                    '%s/etc/minimerge.cfg' % self.path, 'minibuild-0'])
        open('minibuild', 'w').write("""
[minibuild]
install_method=buildout
""")
        class mconfig(dict):
            def __init__(self, *args, **kwargs):
                dict.__init__(self, *args, **kwargs)
                self._sections = {'minibuild':{'buildout_parts': ''}}
        minibuild = api.Minibuild('minibuild')
        minibuild.category = 'eggs'
        minibuild.name = 'toto'
        minibuild.minibuild_config = mconfig()
        mf = makers.interfaces.IMakerFactory(self.config)
        buildout = mf('buildout')
        pyvers = {'python_versions': ['2.4', '2.5']}
        options = buildout.get_options(minimerge, minibuild, **pyvers)
        self.assertEquals(options['parts'],[])
        minibuild.category = 'dependencies'
        options = buildout.get_options(minimerge, minibuild, **pyvers)
        minibuild.category = 'zope'
        options = buildout.get_options(minimerge, minibuild, **pyvers)
        self.assertEquals(options['parts'], [])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBuildout))
    return suite

# vim:set et sts=4 ts=4 tw=80:
