__docformat__ = 'restructuredtext en'

import unittest
import shutil
import os
import tempfile

from minitage.core.unpackers import interfaces

from minitage.core.tests import base

class testZip(base.TestCase):
    """testZip."""

    def setUp(self):
        """."""
        self.path = self.layer['p'] + '/ziptest'
        path = self.path
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)

    def testZipfile(self):
        path = self.path
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
        path = self.path
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

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testZip))
    return suite

# vim:set et sts=4 ts=4 tw=80:
