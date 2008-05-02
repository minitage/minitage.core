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
        minibuild1='''
[minibuild]
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
'''
        minibuild2='''
[minibuild]
depends=minibuild1
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
'''
        minibuild3='''
[minibuild]
depends=minibuild2 minibuild4
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
'''
        minibuild4='''
[minibuild]
depends=minibuild2
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
'''
        minibuild5='''
[minibuild]
depends=minibuild3
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
'''
        minibuild6='''
[minibuild]
depends=minibuild8
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
'''
        minibuild7='''
[minibuild]
depends=minibuild6
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
'''
        minibuild8='''
[minibuild]
depends=minibuild7
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
'''
        for index,minibuild in enumerate((minibuild1, minibuild2, minibuild3,
                          minibuild4, minibuild6, minibuild6,
                          minibuild7, minibuild8),):
            open('%s/minibuild%s' % (minilay, index), 'w').write(minibuild)

    def tearDown(self):
        shutil.rmtree(os.path.expanduser(path))

    def atestFindMinibuild(self):
        # create minilays in the minilays dir, seeing if they get putted in
        sys.argv = [sys.argv[0], '--config', '%s/etc/minimerge.cfg' % path, 'foo']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        mb = minimerge._find_minibuild('minibuild0')
        self.assertEquals('minibuild0', mb.name)

    def atestComputeDepsWithNoDeps(self):
        sys.argv = [sys.argv[0], '--config', '%s/etc/minimerge.cfg' % path, 'foo']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        minimerge._compute_dependencies(['minibuild0'])
        mb = minimerge.computed_packages[0]
        self.assertEquals('minibuild0', mb.name)

    def testMinibuildNotFound(self):
        sys.argv = [sys.argv[0], '--config', '%s/etc/minimerge.cfg' % path, 'foo']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        import pdb;pdb.set_trace()  ## Breakpoint ##
        self.assertRaises(core.MinibuildNotFoundError, minimerge._find_minibuild, 'INOTINANYMINILAY') 


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testMinilays))
    unittest.TextTestRunner(verbosity=2).run(suite)

