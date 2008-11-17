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

from minitage.core.fetchers import interfaces
from minitage.core.fetchers import static as staticm

opts = dict(
    path=os.path.expanduser(tempfile.mkdtemp()),
    dest=os.path.expanduser(tempfile.mkdtemp()),
)

prefix = os.getcwd()

class testStatic(unittest.TestCase):
    """testStatic"""

    def setUp(self):
        """."""
        os.chdir(prefix)
        for dir in [ opts['path'], opts['dest']]:
            if not os.path.isdir(dir):
                os.makedirs(dir)
        f = open('%(path)s/file' % opts, 'w')
        f.write('666')
        f.flush()
        f.close()

    def tearDown(self):
        """."""
        for dir in [ opts['path'], opts['dest']]:
            if os.path.isdir(dir):
                shutil.rmtree(dir)

    def testFetch(self):
        """testFetch"""
        static = staticm.StaticFetcher()
        static.fetch(opts['dest'],'file://%s/file' % opts['path'])
        self.assertTrue(os.path.isdir('%s/%s' % (opts['dest'], '.download')))
        self.assertTrue(os.path.isfile('%s/%s' % (opts['dest'], '.download/file')))
        self.assertTrue(os.path.isfile('%s/%s' % (opts['dest'], 'file')))
        self.assertEquals(open('%s/%s' % (opts['dest'], 'file')).read(),
                               '666')

    def testProxysConfig(self):
        """testProxysConfig."""
        static = staticm.StaticFetcher({'minimerge': {'http-proxies': 'a a a'}})
        self.assertEquals(static._proxies, ['a', 'a', 'a'])

def test_suite():            
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testStatic))
    return suite 

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testStatic))
    unittest.TextTestRunner(verbosity=2).run(suite)

# vim:set et sts=4 ts=4 tw=80:
