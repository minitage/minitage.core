__docformat__ = 'restructuredtext en'

import unittest
import shutil
import os
import tempfile

from minitage.core.unpackers import interfaces

opts = dict()
path = tempfile.mkdtemp()

from minitage.core.tests import base

class testTar(base.TestCase):
    """testtar"""

    def setUp(self):
        opts.update(dict(
            path=os.path.expanduser('%(p)s/minitagerepo') % self.layer,
            dest=os.path.expanduser('%(p)s/minitagerepodest') % self.layer,
            wc=os.path.expanduser('%(p)s/minitagerepodestwc') % self.layer,
        ))
        for k in opts:
            path = opts[k]
            if os.path.exists(path):
                shutil.rmtree(path)
            os.makedirs(path)


    def testTarfile(self):
        """testTarfile."""
        path = opts['path']
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
        path = opts['path']
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
        path = opts['path']
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


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testTar))
    return suite

# vim:set et sts=4 ts=4 tw=80:
