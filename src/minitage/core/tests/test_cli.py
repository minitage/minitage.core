__docformat__ = 'restructuredtext en'

import unittest
import sys
import os
import tempfile
import shutil


from minitage.core import core, cli, api
from minitage.core.tests.base import TestCase

class TestCli(TestCase):
    """Test cli usage for minimerge."""


    def setUp(self):
        self.argv = sys.argv

    def tearDown(self):
        sys.argv = self.argv

    def testCLIActions(self):
        """Test minimerge actions."""
        path = self.layer['p']
        actions = {'-R': 'reinstall',
                   '--rm': 'delete',
                   '--install': 'install',
                   '--sync': 'sync'}
        actions = {
                   '--sync': 'sync'}
        sys.argv = [sys.argv[0], '--config', 'non existing', 'foo']
        self.assertRaises(core.InvalidConfigFileError, cli.do_read_options, read_options=True)
        sys.argv = [sys.argv[0], '--sync', '--config', os.path.join(path, 'etc', 'minimerge.cfg'), 'foo']
        opts = cli.do_read_options(read_options=True)
        minimerge = api.Minimerge(opts)
        self.assertEquals(getattr(minimerge, '_action'), 'sync')
        for action in actions:
            sys.argv = [sys.argv[0], action, '--config', os.path.join(path, 'etc', 'minimerge.cfg'), 'foo']
            opts = cli.do_read_options(read_options=True)
            self.assertEquals(getattr(minimerge, '_action'), opts['action'])


        sys.argv = [sys.argv[0], '--config', os.path.join(path, 'etc', 'minimerge.cfg'), 'foo']
        opts = cli.do_read_options(read_options=True)
        minimerge = api.Minimerge(opts)
        self.assertEquals(getattr(minimerge, '_action'), opts['action'])

        sys.argv = [sys.argv[0], '--config', os.path.join(path, 'etc', 'minimerge.cfg'), '--rm']
        self.assertRaises(core.NoPackagesError, cli.do_read_options, read_options=True)

        sys.argv = [sys.argv[0], '--config', os.path.join(path, 'etc', 'minimerge.cfg'), '--reinstall', '--rm', 'foo']
        self.assertRaises(core.ConflictModesError, cli.do_read_options, read_options=True, pdb=True)

        sys.argv = [sys.argv[0], '--config', os.path.join(path, 'etc', 'minimerge.cfg'), '--reinstall', '--rm', 'foo']
        self.assertRaises(core.ConflictModesError, cli.do_read_options, read_options=True)

        sys.argv = [sys.argv[0], '--config', os.path.join(path, 'etc', 'minimerge.cfg'), '--fetchonly', '--offline', 'foo']
        self.assertRaises(core.ConflictModesError, cli.do_read_options, read_options=True)

        sys.argv = [sys.argv[0], '--config', os.path.join(path, 'etc', 'minimerge.cfg'), '--jump', 'foo', '--nodeps', 'foo']
        self.assertRaises(core.ConflictModesError, cli.do_read_options, read_options=True)

        sys.argv = [sys.argv[0], '--config', os.path.join(path, 'etc', 'minimerge.cfg'), '--reinstall', '--config',
                    'iamafilewhichdoesnotexist', 'foo']
        self.assertRaises(core.InvalidConfigFileError, cli.do_read_options, read_options=True)

    def testModes(self):
        """Test minimerge modes."""
        path = self.layer['p']
        modes = ('offline', 'fetchonly', 'ask',
                 'debug', 'nodeps', 'pretend')
        for mode in modes:
            sys.argv = [sys.argv[0], '--%s' % mode, '--config' , os.path.join(path, 'etc', 'minimerge.cfg'), 'foo']
            opts = cli.do_read_options(read_options=True)
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

