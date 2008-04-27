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
from minitage.core import core, cli
import test_common

class testMinilays(unittest.TestCase):
    """ test cli usage for minimerge"""

    def testMinilays(self):
        path = os.path.expanduser('~/iamauniquetestdirformatiwillberemoveafterthetest')
        testopts = dict(path=path)
        test_common.createMinitageEnv(path)
        
        # create minilays in the minilays dir, seeing if they get putted in
        minilays = []
        minilays.append('%(path)s/minilays/myminilay1' % testopts)
        for minilay in minilays:
            os.system('mkdir -p %s' % minilay)
        sys.argv = [sys.argv[0], '--config', '%s/etc/minimerge.cfg'%path, 'foo']
        opts = cli.do_read_options()
        minimerge = core.Minimerge(opts)
        for dir in minilays:
            self.failUnless(dir in minimerge.minilays)

        # create minilays in env. seeing if they get putted in
        minilays = []
        minilays.append('%(path)s/minilays_alternate/myminilay1' % testopts)
        for minilay in minilays:
            os.system('mkdir -p %s' % minilay)
            os.environ['MINILAYS'] = '%s %s' % (minilay, os.environ.get('MINILAYS',''))
        sys.argv = [sys.argv[0], '--config', '%s/etc/minimerge.cfg'%path, 'foo']
        opts = cli.do_read_options()
        minimerge = core.Minimerge(opts)
        for dir in minilays:
            self.failUnless(dir in minimerge.minilays) 
        # reset env
        os.environ['MINILAYS'] = ''
        
        # create minilays in the config. seeing if they get putted in
        minilays = []
        minilays.append('%(path)s/minilays_alternate2/myminilay1' % testopts)
        for minilay in minilays:
            os.system('''
                      echo 'minilays=%s' >> %s/etc/minimerge.cfg
                      mkdir -p %s 
                     ''' % (minilay, path, minilay))
        sys.argv = [sys.argv[0], '--config', '%s/etc/minimerge.cfg' % path, 'foo']
        opts = cli.do_read_options()
        minimerge = core.Minimerge(opts)
        for dir in minilays:
            self.failUnless(dir in minimerge.minilays)  
        shutil.rmtree(os.path.expanduser(path))

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testMinilays))
    unittest.TextTestRunner(verbosity=2).run(suite)

