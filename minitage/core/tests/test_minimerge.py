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
from minitage.core import api, cli, objects, core
import test_common

path = os.path.expanduser('~/iamauniquetestdirformatiwillberemoveafterthetest')
testopts = dict(path=path)
minilay = '%(path)s/minilays/myminilay1' % testopts
class testMinilays(unittest.TestCase):

    def setUp(self):
        test_common.createMinitageEnv(path)
        os.system('mkdir -p %s' % minilay)
        minibuild0="""
[minibuild]
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
"""
        minibuild1="""
[minibuild]
depends=minibuild-0
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
"""
        minibuild2="""
[minibuild]
depends=minibuild-4 minibuild-1
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
"""
        minibuild3="""
[minibuild]
depends=minibuild-2
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
"""
        minibuild4="""
[minibuild]
depends=minibuild-0
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
"""
        minibuild5="""
[minibuild]
depends=minibuild-7
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
"""
        minibuild6="""
[minibuild]
depends=minibuild-5
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
"""
        minibuild7="""
[minibuild]
depends=minibuild-6
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
"""
        minibuild8="""
[minibuild]
depends=minibuild-8
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
"""
        minibuild9="""
[minibuild]
depends=minibuild-0 minibuild-3
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
"""
        minibuild10="""
[minibuild]
depends=minibuild-11
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
"""
        minibuild11="""
[minibuild]
depends=minibuild-12
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
"""
        minibuild12="""
[minibuild]
depends=minibuild-13
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
"""
        minibuild13="""
[minibuild]
depends=minibuild-10
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
"""
        for index,minibuild in enumerate((minibuild0, minibuild1, minibuild2, minibuild3,
                         minibuild4, minibuild5, minibuild6, minibuild7, minibuild8,
                         minibuild9, minibuild10, minibuild11, minibuild12, minibuild13),):
            open('%s/minibuild-%s' % (minilay, index), 'w').write(minibuild)

    def tearDown(self):
        shutil.rmtree(os.path.expanduser(path))

    def testFindMinibuild(self):
        """find m0?"""
        # create minilays in the minilays dir, seeing if they get putted in
        sys.argv = [sys.argv[0], '--config', '%s/etc/minimerge.cfg' % path, 'foo']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        mb = minimerge._find_minibuild('minibuild-0')
        self.assertEquals('minibuild-0', mb.name)

    def testComputeDepsWithNoDeps(self):
        """m0 depends on nothing"""
        sys.argv = [sys.argv[0], '--config', '%s/etc/minimerge.cfg' % path, 'foo']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        computed_packages = minimerge._compute_dependencies(['minibuild-0'])
        mb = computed_packages[0]
        self.assertEquals('minibuild-0', mb.name)

    def testSimpleDeps(self):
        """ test m1 -> m0"""
        sys.argv = [sys.argv[0], '--config', '%s/etc/minimerge.cfg' % path, 'foo']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        computed_packages = minimerge._compute_dependencies(['minibuild-1'])
        mb = computed_packages[0]
        self.assertEquals(mb.name, 'minibuild-0')
        mb = computed_packages[1]
        self.assertEquals(mb.name, 'minibuild-1')

    def testChainedandTreeDeps(self):
        """ Will test that this tree is safe:
              -       m3
                      /
                     m2
                     / \
                    m4 m1
                     \/
                     m0

               -   m9
                  / \
                 m0 m3
        """
        sys.argv = [sys.argv[0], '--config', '%s/etc/minimerge.cfg' % path, 'foo']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        computed_packages = minimerge._compute_dependencies(['minibuild-3'])
        wanted_list = ['minibuild-0', 'minibuild-4', 'minibuild-1', 'minibuild-2', 'minibuild-3']
        self.assertEquals([mb.name for mb in computed_packages], wanted_list)
        computed_packages = minimerge._compute_dependencies(['minibuild-9'])
        wanted_list = ['minibuild-0', 'minibuild-4', 'minibuild-1', 'minibuild-2', 'minibuild-3','minibuild-9']
        self.assertEquals([mb.name for mb in computed_packages], wanted_list)


    def testRecursivity(self):
        """check that:
             - m5  -> m6 -> m7
             - m8  -> m8
             - m10 -> m11 -> m12 -> m13 -> m10
        will throw some recursity problems.
        """
        sys.argv = [sys.argv[0], '--config', '%s/etc/minimerge.cfg' % path, 'foo']
        opts = cli.do_read_options()

        minimerge = api.Minimerge(opts)
        self.assertRaises(core.CircurlarDependencyError, minimerge._compute_dependencies, ['minibuild-6'])

        minimerge = api.Minimerge(opts)
        self.assertRaises(core.CircurlarDependencyError, minimerge._compute_dependencies, ['minibuild-8'])

        minimerge = api.Minimerge(opts)
        self.assertRaises(core.CircurlarDependencyError, minimerge._compute_dependencies, ['minibuild-13'])

    def testMinibuildNotFound(self):
        """ INOTINANYMINILAY does not exist"""
        sys.argv = [sys.argv[0], '--config', '%s/etc/minimerge.cfg' % path, 'foo']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        self.assertRaises(core.MinibuildNotFoundError, minimerge._find_minibuild, 'INOTINANYMINILAY')

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testMinilays))
    unittest.TextTestRunner(verbosity=2).run(suite)


