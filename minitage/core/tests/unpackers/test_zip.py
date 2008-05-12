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

prefix = os.getcwd()

path = tempfile.mkdtemp()

class testZip(unittest.TestCase):
    """testZip."""

    def tearDown(self):
        """."""
        shutil.rmtree(path)
        os.makedirs(path)

    def testZipfile(self):
        """testZipfile."""
        os.chdir(path)
        os.system("""
                  mkdir a b;
                  echo "aaaa"> a/toto;
                  zip -qr toto.zip a;
                  rm -rf a""")
        self.assertFalse(os.path.isdir('a'))
        f = interfaces.IUnpackerFactory()
        zip = f('%s/toto.zip' % path)
        zip.unpack('%s/toto.zip' % path)
        zip.unpack('%s/toto.zip' % path, '%s/b' % path)
        self.assertTrue(os.path.isfile('a/toto'))
        self.assertEquals(open('a/toto').read(),'aaaa\n')
        self.assertTrue(os.path.isfile('b/a/toto'))

    def DesactivatedtestBz2file(self):
        """testTarbz2file."""
        os.chdir(path)
        os.system("""
                  mkdir a;
                  echo "aaaa"> a/toto;
                  bzip2 -kcz a/toto>toto.bz2;
                  rm -rf a""")
        self.assertFalse(os.path.isdir('a'))
        f = interfaces.IUnpackerFactory()
        tar = f('%s/toto.bz2' % path)
        tar.unpack('%s/toto.bz2' % path)
        self.assertTrue(os.path.isfile('toto'))
        self.assertEquals(open('a/toto').read(),'aaaa\n')

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testZip))
    unittest.TextTestRunner(verbosity=2).run(suite)

# vim:set et sts=4 ts=4 tw=80:
