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
import optparse
import ConfigParser

from minitage.core import core, cli, api

class testCli(unittest.TestCase):
    """ test cli usage for minimerge"""

    def testActions(self):
        actions = {'-R': 'rebuild', '--rm': 'remove', '--install': 'install','--sync':'sync'}
        for action in actions:
            sys.argv = [sys.argv[0], action, 'foo']
            opts = cli.do_read_options()
            minimerge = api.Minimerge(opts)
            self.assertEquals(minimerge.action, opts['action'])

        sys.argv = [sys.argv[0], 'foo']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        self.assertEquals(minimerge.action, opts['action'])

        sys.argv = [sys.argv[0], '--rm']
        self.assertRaises(core.NoPackagesError, cli.do_read_options)

        sys.argv = [sys.argv[0],'--install', '--rm', 'foo']
        self.assertRaises(core.TooMuchActionsError, cli.do_read_options)

        sys.argv = [sys.argv[0],'--rebuild', '--rm', 'foo']
        self.assertRaises(core.ConflictModesError, cli.do_read_options)

        sys.argv = [sys.argv[0],'--fetchonly', '--offline', 'foo']
        self.assertRaises(core.ConflictModesError, cli.do_read_options)

        sys.argv = [sys.argv[0],'--jump', 'foo', '--nodeps', 'foo']
        self.assertRaises(core.ConflictModesError, cli.do_read_options)

        sys.argv = [sys.argv[0],'--rebuild', '--config', 'iamafilewhichdoesnotexist', 'foo']
        self.assertRaises(core.InvalidConfigFileError, cli.do_read_options)

    def testModes(self):
        modes = ('offline', 'fetchonly', 'debug', 'nodeps')
        for mode in modes:
            sys.argv = [sys.argv[0], '--%s' % mode, 'foo']
            opts = cli.do_read_options()
            minimerge = api.Minimerge(opts)
            self.assertTrue(getattr(minimerge, mode, False))

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testCli))
    unittest.TextTestRunner(verbosity=2).run(suite)

