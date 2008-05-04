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

from minitage.core.fetchers import scm, interfaces

opts = dict(
    path=os.path.expanduser('~/minitagerepo'),
    dest=os.path.expanduser('~/minitagerepodest'),
)

class testHg(unittest.TestCase):

    def setUp(self):
        # make an hg repo
        os.system("""
                 mkdir -p  %(path)s         2>&1 >> /dev/null
                 cd %(path)s                2>&1 >> /dev/null
                 echo '666'>file            2>&1 >> /dev/null
                 hg init                    2>&1 >> /dev/null
                 hg add                     2>&1 >> /dev/null
                 hg ci -m 'initial import'  2>&1 >> /dev/null
                 echo '666'>file2           2>&1 >> /dev/null
                 hg add                     2>&1 >> /dev/null
                 hg ci -m 'second revision' 2>&1 >> /dev/null
                 """ % opts)

    def tearDown(self):
        for dir in [ opts['path'], opts['dest']]:
            if os.path.isdir(dir):
                shutil.rmtree(dir)

    def testScmInvalidUri(self):
        hg = scm.HgFetcher()
        self.assertRaises(interfaces.InvalidUrlError,hg.fetch, 'invalidsrcuri', 'somewhere')

    def testInvalidReturn(self):
        hg = scm.HgFetcher()
        hg.executable = 'nothg'
        # shell will not find that command, heh
        self.assertRaises(interfaces.FetcherRuntimmeError, hg.fetch, 'file://nowhere', 'somewhere')

        hg = scm.HgFetcher()
        # prevent mercurial from writing in dest ;)
        os.mkdir(opts['dest'],660)
        # it will crash luke
        self.assertRaises(interfaces.FetcherRuntimmeError, hg.fetch, 'file://%s' % opts['path'], opts['dest'])
        os.removedirs(opts['dest'])

    def testFetch(self):
        hg = scm.HgFetcher()
        hg.fetch('file://%s' % opts['path'], opts['dest'])
        self.assertTrue(os.path.isdir('%s/%s' % (opts['dest'], '.hg')))

    def testFetchToParticularRevision(self):
        hg = scm.HgFetcher()
        hg.fetch('file://%s' % opts['path'], opts['dest'], dict(revision=0))
        self.assertTrue(os.path.isdir('%s/%s' % (opts['dest'], '.hg')))
        self.assertFalse(os.path.isfile('%s/%s' % (opts['dest'], 'file2')))

    def testUpdate(self):
        hg = scm.HgFetcher()
        hg.fetch('file://%s' % opts['path'], opts['dest'],dict(revision=0))
        self.assertTrue(os.path.isdir('%s/%s' % (opts['dest'], '.hg')))
        hg.update('file://%s' % opts['path'], opts['dest'])
        self.assertTrue(os.path.isfile('%s/%s' % (opts['dest'], 'file2')))
        hg.update('file://%s' % opts['path'], opts['dest'],dict(revision=0))
        self.assertFalse(os.path.isfile('%s/%s' % (opts['dest'], 'file2')))

    def testFetchOrUpdate_fetch(self):
        hg = scm.HgFetcher()
        hg.fetch_or_update('file://%s' % opts['path'], opts['dest'])
        self.assertTrue(os.path.isfile('%s/%s' % (opts['dest'], 'file2')))
        self.assertTrue(os.path.isdir('%s/%s' % (opts['dest'], '.hg')))

    def testFetchOrUpdate_update(self):
        hg = scm.HgFetcher()
        hg.fetch('file://%s' % opts['path'], opts['dest'],dict(revision=0))
        self.assertTrue(os.path.isdir('%s/%s' % (opts['dest'], '.hg')))
        self.assertFalse(os.path.isfile('%s/%s' % (opts['dest'], 'file2')))
        hg.fetch_or_update('file://%s' % opts['path'], opts['dest'])
        self.assertTrue(os.path.isfile('%s/%s' % (opts['dest'], 'file2')))

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testHg))
    unittest.TextTestRunner(verbosity=2).run(suite)

# vim:set et sts=4 ts=4 tw=80:
