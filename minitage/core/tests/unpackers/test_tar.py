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

import unittest
import shutil
import os
import tempfile

from minitage.core.unpackers import interfaces

opts = dict(
    path=os.path.expanduser('~/minitagerepo'),
    dest=os.path.expanduser('~/minitagerepodest'),
    wc=os.path.expanduser('~/minitagerepodestwc'),
)

prefix = os.getcwd()

path = tempfile.mkdtemp()

class testTar(unittest.TestCase):
    """testtar"""

    def tearDown(self):
        """."""
        shutil.rmtree(path)
        os.makedirs(path)

    def testTarfile(self):
        """testTarfile."""
        os.chdir(path)
        os.system("""
                  mkdir a b;
                  echo "aaaa"> a/toto;
                  tar -cf toto.tar a;
                  rm -rf a""")
        self.assertFalse(os.path.isdir('a'))
        f = interfaces.IUnpackerFactory()
        tar = f('%s/toto.tar' % path)
        tar.unpack('%s/toto.tar' % path)
        tar.unpack('%s/toto.tar' % path, '%s/b' % path)
        self.assertTrue(os.path.isfile('a/toto'))
        self.assertTrue(os.path.isfile('b/a/toto'))
        self.assertEquals(open('a/toto').read(),'aaaa\n')

    def testTarbz2file(self):
        """testTarbz2file."""
        os.chdir(path)
        os.system("""
                  mkdir a;
                  echo "aaaa"> a/toto;
                  tar -cjf toto.tbz2 a;
                  rm -rf a""")
        self.assertFalse(os.path.isdir('a'))
        f = interfaces.IUnpackerFactory()
        tar = f('%s/toto.tbz2' % path)
        tar.unpack('%s/toto.tbz2' % path)
        self.assertTrue(os.path.isfile('a/toto'))
        self.assertEquals(open('a/toto').read(),'aaaa\n')

    def testTargzfile(self):
        """testTargzfile."""
        os.chdir(path)
        os.system("""
                  mkdir a;
                  echo "aaaa"> a/toto;
                  tar -czf toto.tgz a;
                  rm -rf a""")
        self.assertFalse(os.path.isdir('a'))
        f = interfaces.IUnpackerFactory()
        tar = f('%s/toto.tgz' % path)
        tar.unpack('%s/toto.tgz' % path)
        self.assertTrue(os.path.isfile('a/toto'))
        self.assertEquals(open('a/toto').read(),'aaaa\n')

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testTar))
    unittest.TextTestRunner(verbosity=2).run(suite)

# vim:set et sts=4 ts=4 tw=80:
