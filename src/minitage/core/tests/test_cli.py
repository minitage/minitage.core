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
import sys
import os
import tempfile
import shutil

from minitage.core import core, cli, api
from minitage.core.tests import test_common 


path = os.path.expanduser(tempfile.mkdtemp())
shutil.rmtree(path)

class TestCli(unittest.TestCase):
    """Test cli usage for minimerge."""
    def setUp(self):
        """."""
        test_common.createMinitageEnv(path)

    def tearDown(self):
        """."""
        shutil.rmtree(os.path.expanduser(path)) 
    
    def testActions(self):
        """Test minimerge actions."""
        actions = {'-R': 'reinstall',
                   '--rm': 'delete',
                   '--install': 'install',
                   '--sync': 'sync'}
        sys.argv = [sys.argv[0], '-c', 'non existing', 'foo']
        self.assertRaises(core.InvalidConfigFileError, cli.do_read_options)
        for action in actions:
            sys.argv = [sys.argv[0], action, '--config', os.path.join(path, 'etc', 'minimerge.cfg'), 'foo']
            opts = cli.do_read_options()
            minimerge = api.Minimerge(opts)
            self.assertEquals(getattr(minimerge, '_action'), opts['action'])

        sys.argv = [sys.argv[0], '--config', os.path.join(path, 'etc', 'minimerge.cfg'), 'foo']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        self.assertEquals(getattr(minimerge, '_action'), opts['action'])

        sys.argv = [sys.argv[0], '--config', os.path.join(path, 'etc', 'minimerge.cfg'), '--rm']
        self.assertRaises(core.NoPackagesError, cli.do_read_options)

        sys.argv = [sys.argv[0], '--config', os.path.join(path, 'etc', 'minimerge.cfg'), '--install', '--rm', 'foo']
        self.assertRaises(core.TooMuchActionsError, cli.do_read_options)

        sys.argv = [sys.argv[0], '--config', os.path.join(path, 'etc', 'minimerge.cfg'), '--reinstall', '--rm', 'foo']
        self.assertRaises(core.ConflictModesError, cli.do_read_options)

        sys.argv = [sys.argv[0], '--config', os.path.join(path, 'etc', 'minimerge.cfg'), '--fetchonly', '--offline', 'foo']
        self.assertRaises(core.ConflictModesError, cli.do_read_options)

        sys.argv = [sys.argv[0], '--config', os.path.join(path, 'etc', 'minimerge.cfg'), '--jump', 'foo', '--nodeps', 'foo']
        self.assertRaises(core.ConflictModesError, cli.do_read_options)

        sys.argv = [sys.argv[0], '--config', os.path.join(path, 'etc', 'minimerge.cfg'), '--reinstall', '--config',
                    'iamafilewhichdoesnotexist', 'foo']
        self.assertRaises(core.InvalidConfigFileError, cli.do_read_options)

    def testModes(self):
        """Test minimerge modes."""
        modes = ('offline', 'fetchonly', 'ask',
                 'debug', 'nodeps', 'pretend')
        for mode in modes:
            sys.argv = [sys.argv[0], '--%s' % mode, '--config' , os.path.join(path, 'etc', 'minimerge.cfg'), 'foo']
            opts = cli.do_read_options()
            minimerge = api.Minimerge(opts)
            self.assertTrue(getattr(minimerge, '_%s' % mode, False))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCli))
    return suite

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCli))
    unittest.TextTestRunner(verbosity=2).run(suite)

