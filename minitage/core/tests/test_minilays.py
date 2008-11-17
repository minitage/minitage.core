# Copyright (C) 2008, 'Mathieu PASQUET <kiorky@cryptelium.net>'
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

__docformat__ = 'restructuredtext en'

import unittest
import os
import sys
import shutil
import optparse
import ConfigParser
import re
import tempfile

from minitage.core import api, cli, objects
from minitage.core.tests import test_common

path = os.path.expanduser(tempfile.mkdtemp())
shutil.rmtree(path)
testopts = dict(path=path)
minilay1 = '%(path)s/minilays/myminilay1' % testopts
class testMinilays(unittest.TestCase):
    """testMinilays"""

    def setUp(self):
        """."""
        test_common.createMinitageEnv(path)
        os.system('mkdir -p %s' % minilay1)

    def tearDown(self):
        """."""
        shutil.rmtree(os.path.expanduser(path))

    def testSearchingForMinilays(self):
        """testSearchingForMinilays"""
        # create minilays in the minilays dir, seeing if they get putted in
        sys.argv = [sys.executable, '--config',
                    '%s/etc/minimerge.cfg' % path, 'foo']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        self.failUnless(minilay1
                        in [minilay.path for minilay in minimerge._minilays])

        # create minilays in env. seeing if they get putted in
        minilays = []
        minilays.append('%(path)s/minilays_alternate/myminilay1' % testopts)
        for minilay in minilays:
            os.system('mkdir -p %s' % minilay)
            os.environ['MINILAYS'] = '%s %s' % (
                minilay, os.environ.get('MINILAYS','')
            )
        sys.argv = [sys.argv[0], '--config',
                    '%s/etc/minimerge.cfg' % path, 'foo']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        for dir in minilays:
            self.failUnless(dir
                           in [minilay.path for minilay in minimerge._minilays])
        # reset env
        os.environ['MINILAYS'] = ''

        # create minilays in the config. seeing if they get putted in
        minilays = []
        minilays.append('%(path)s/minilays_alternate2/myminilay1' % testopts)
        f = open('%s/etc/minimerge.cfg' % path,'r').read()
        for minilay in minilays:
            f = re.sub('(#\s*minilays\s*=)(.*)',
                       'minilays= \\2 %s' % minilay, f)
            os.system("mkdir -p %s" % (minilay))
        open('%s/etc/minimerge.cfg'%path,'w').write(f)
        sys.argv = [sys.argv[0], '--config',
                    '%s/etc/minimerge.cfg' % path, 'foo']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        for dir in minilays:
            self.failUnless(dir
                           in [minilay.path for minilay in minimerge._minilays])

    def testLoadingBrokenMinibuild(self):
        """testLoadingBrokenMinibuild"""
        # create minilays in the minilays dir, seeing if they get putted in
        minibuild = """
[minibuild]
dependencies=python
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=in/va/lid
"""
        open('%s/minibuild-1' % minilay1, 'w').write(minibuild)
        minilay = api.Minilay(path=minilay1)
        self.assertTrue( None == minilay['minibuild-1'].loaded)
        self.assertRaises(objects.InvalidCategoryError,
                          minilay['minibuild-1'].load)

        minibuild = """
[minibuild]
dependencies=python
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
"""
        open('%s/minibuild-1' % minilay1, 'w').write(minibuild)
        minilay = api.Minilay(path=minilay1)
        self.assertTrue(isinstance(minilay['minibuild-1'], objects.Minibuild))
        self.assertEquals(minilay['minibuild-1'].name, 'minibuild-1')

    def testInvalidMinilayPath(self):
        """testInvalidMinilayPath"""
        self.assertRaises(objects.InvalidMinilayPath,
                          api.Minilay, path='notexistingpath')

    def testLazyLoad(self):
        """testLazyLoad"""
        minibuild = """
[minibuild]
dependencies=python
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
"""
        open('%s/minibuild-1' % minilay1, 'w').write(minibuild)
        minilay = api.Minilay(path=minilay1)
        self.assertFalse('minibuild-1' in minilay.keys())
        a = minilay['minibuild-1']
        self.assertTrue('minibuild-1' in minilay.keys())

        minilay2 = api.Minilay(path=minilay1)
        self.assertTrue('minibuild-1' in minilay2)
        self.assertFalse('minibuild-2' in minilay2)

    def testMinibuildNotInMinilay(self):
        """testMinibuildNotInMinilay"""
        minilay = api.Minilay(path=minilay1)
        minilay.load()
        self.assertTrue('minibuild-1' not in minilay)

    def testMinibuildInMinilay(self):
        """testMinibuildInMinilay"""
        minibuild = """
[minibuild]
dependencies=python
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
"""
        open('%s/minibuild-1' % minilay1, 'w').write(minibuild)
        minilay = api.Minilay(path=minilay1)
        minilay.load()
        self.assertTrue('minibuild-1' in minilay)
        self.assertTrue('minibuild-2' not in minilay)

    def testLoad(self):
        """testLoad"""
        minibuild = """
[minibuild]
dependencies=python
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
"""
        l = ['minibuild-1', 'minibuild-2', 'minibuild-3', 'minibuild-4']
        for m in l:
            open('%s/%s' % (minilay1, m), 'w').write(minibuild)
        minilay = api.Minilay(path=minilay1)
        for m in l:
            self.assertFalse(m in minilay.keys())
        minilay.load()
        for m in l:
            self.assertTrue(m in minilay.keys())
        self.assertTrue(minilay.loaded)

        minilay2 = api.Minilay(path=minilay1)
        for m in l:
            self.assertFalse(m in minilay2.keys())
        a = minilay2['minibuild-1']
        b = minilay2['minibuild-2']
        for m in ['minibuild-1', 'minibuild-2']:
            self.assertTrue(m in minilay2.keys())
        for m in ['minibuild-3', 'minibuild-4']:
            self.assertFalse(m in minilay2.keys())
        self.assertFalse(minilay2.loaded)

def test_suite():            
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testMinilays)) 
    return suite       

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testMinilays))
    unittest.TextTestRunner(verbosity=2).run(suite)

