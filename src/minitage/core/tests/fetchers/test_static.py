__docformat__ = 'restructuredtext en'

import unittest
import shutil
import os
import tempfile

from minitage.core.fetchers import interfaces
from minitage.core.fetchers import static as staticm

from minitage.core.tests import base

class testStatic(base.TestCase):
    """testStatic"""

    def setUp(self):
        """."""
        prefix = self.layer['p']
        self.opts = opts = dict(
            path=os.path.join(prefix, 'statis1'),
            dest=os.path.join(prefix, 'statis2'),
            wc=os.path.join(prefix, 'statis3'),
            path3=os.path.join(prefix, 'statis4'),
            path2=os.path.join(prefix, 'statis5'),
        )
        for dir in [ opts['path'], opts['dest']]:
            if not os.path.isdir(dir):
                os.makedirs(dir)
        f = open('%(path)s/file' % opts, 'w')
        f.write('666')
        f.flush()
        f.close()

    def tearDown(self):
        """."""
        opts = self.opts
        if 'http_proxy' in os.environ:
            del os.environ['http_proxy']
        for dir in [ opts['path'], opts['dest']]:
            if os.path.isdir(dir):
                shutil.rmtree(dir)

    def testFetch(self):
        """testFetch"""
        opts = self.opts
        static = staticm.StaticFetcher()
        static.fetch(opts['dest'],'file://%s/file' % opts['path'])
        self.assertTrue(os.path.isdir('%s/%s' % (opts['dest'], '.download')))
        self.assertTrue(os.path.isfile('%s/%s' % (opts['dest'], '.download/file')))
        self.assertTrue(os.path.isfile('%s/%s' % (opts['dest'], 'file')))
        self.assertEquals(open('%s/%s' % (opts['dest'], 'file')).read(),
                               '666')

    def testProxysConfig(self):
        """testProxysConfig."""
        opts = self.opts
        static = staticm.StaticFetcher({'minimerge': {'http_proxy': 'a a a'}})
        self.assertEquals(os.environ['http_proxy'], 'a a a')
        if 'http_proxy' in os.environ:
            del os.environ['http_proxy']

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testStatic))
    return suite

# vim:set et sts=4 ts=4 tw=80:
