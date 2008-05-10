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
    wc=os.path.expanduser('~/minitagerepodestwc'),
)

prefix = os.getcwd()

class testHg(unittest.TestCase):
    """testHg"""

    def setUp(self):
        """."""
        os.chdir(prefix)
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
        """."""
        for dir in [ opts['path'], opts['dest']]:
            if os.path.isdir(dir):
                shutil.rmtree(dir)

    def testUrlChanged(self):
        """testUrlChanged"""
        hg = scm.HgFetcher()
        hg.fetch('file://%s' % opts['path'], opts['dest'])
        self.assertTrue(os.path.isdir('%s/%s' % (opts['dest'], '.hg')))
        self.assertFalse(
            hg._has_uri_changed(
                'file://%s' % opts['path'],
                opts['dest']
            )
        )
        self.assertTrue(hg._has_uri_changed('hehe_changed', opts['dest']))

    def testRemoveVersionnedDirs(self):
        """testRemoveVersionnedDirs"""
        hg = scm.HgFetcher()
        hg.fetch('file://%s' % opts['path'], opts['dest'])
        self.assertTrue(os.path.isdir('%s/%s' % (opts['dest'], '.hg')))
        os.mkdir('%s/%s' % (opts['dest'],'part'))
        hg._remove_versionned_directories(opts['dest'])
        self.assertTrue(os.path.isdir('%s/%s' % (opts['dest'],'part')))
        self.assertFalse(os.path.isdir('%s/%s' % (opts['dest'],'.hg')))
        self.assertFalse(os.path.isfile('%s/%s' % (opts['dest'],'file2')))
        hg.update('file://%s' % opts['path'], opts['dest'])
        self.assertTrue(os.path.isdir('%s/%s' % (opts['dest'], '.hg')))

    def testScmInvalidUri(self):
        """testScmInvalidUri"""
        hg = scm.HgFetcher()
        self.assertRaises(interfaces.InvalidUrlError,
                          hg.fetch, 'invalidsrcuri', 'somewhere')

    def testInvalidReturn(self):
        """testInvalidReturn"""
        hg = scm.HgFetcher()
        hg.executable = 'nothg'
        # shell will not find that command, heh
        self.assertRaises(interfaces.FetcherRuntimmeError,
                          hg.fetch, 'file://nowhere', 'somewhere')

        hg = scm.HgFetcher()
        # prevent mercurial from writing in dest ;)
        os.mkdir(opts['dest'], 660)
        # it will crash luke
        self.assertRaises(interfaces.FetcherRuntimmeError,
                          hg.fetch, 'file://%s' % opts['path'], opts['dest'])
        os.removedirs(opts['dest'])

    def testFetch(self):
        """testFetch"""
        hg = scm.HgFetcher()
        hg.fetch('file://%s' % opts['path'], opts['dest'])
        self.assertTrue(os.path.isdir('%s/%s' % (opts['dest'], '.hg')))

    def testFetchToParticularRevision(self):
        """testFetchToParticularRevision"""
        hg = scm.HgFetcher()
        hg.fetch('file://%s' % opts['path'], opts['dest'], dict(revision=0))
        self.assertTrue(os.path.isdir('%s/%s' % (opts['dest'], '.hg')))
        self.assertFalse(os.path.isfile('%s/%s' % (opts['dest'], 'file2')))

    def testUpdate(self):
        """testUpdate"""
        hg = scm.HgFetcher()
        hg.fetch('file://%s' % opts['path'], opts['dest'], dict(revision=0))
        self.assertTrue(os.path.isdir('%s/%s' % (opts['dest'], '.hg')))
        hg.update('file://%s' % opts['path'], opts['dest'])
        self.assertTrue(os.path.isfile('%s/%s' % (opts['dest'], 'file2')))
        hg.update('file://%s' % opts['path'], opts['dest'], dict(revision=0))
        self.assertFalse(os.path.isfile('%s/%s' % (opts['dest'], 'file2')))

    def testFetchOrUpdate_fetch(self):
        """testFetchOrUpdate_fetch"""
        hg = scm.HgFetcher()
        hg.fetch_or_update('file://%s' % opts['path'], opts['dest'])
        self.assertTrue(os.path.isfile('%s/%s' % (opts['dest'], 'file2')))
        self.assertTrue(os.path.isdir('%s/%s' % (opts['dest'], '.hg')))

    def testFetchOrUpdate_update(self):
        """testFetchOrUpdate_update"""
        hg = scm.HgFetcher()
        hg.fetch('file://%s' % opts['path'], opts['dest'], dict(revision=0))
        self.assertTrue(os.path.isdir('%s/%s' % (opts['dest'], '.hg')))
        self.assertFalse(os.path.isfile('%s/%s' % (opts['dest'], 'file2')))
        hg.fetch_or_update('file://%s' % opts['path'], opts['dest'])
        self.assertTrue(os.path.isfile('%s/%s' % (opts['dest'], 'file2')))


class testSvn(unittest.TestCase):
    """testSvn"""

    def setUp(self):
        """."""
        os.chdir(prefix)
        # make an svn repo
        os.system("""
                 mkdir -p  %(path)s                  2>&1 >> /dev/null
                 cd %(path)s                         2>&1 >> /dev/null
                 svnadmin create .                   2>&1 >> /dev/null
                 mkdir -p  %(dest)s                  2>&1 >> /dev/null
                 svn co file://%(path)s %(dest)s     2>&1 >> /dev/null
                 cd %(dest)s                         2>&1 >> /dev/null
                 echo '666'>file                     2>&1 >> /dev/null
                 svn add file                        2>&1 >> /dev/null
                 svn ci -m 'initial import'          2>&1 >> /dev/null
                 cho '666'>file2                    2>&1 >> /dev/null
                 svn add file2                       2>&1 >> /dev/null
                 svn ci -m 'second revision'         2>&1 >> /dev/null
                 svn up                              2>&1 >> /dev/null
                 """ % opts)

    def tearDown(self):
        """."""
        for dir in [opts['wc'], opts['path'], opts['dest']]:
            if os.path.isdir(dir):
                shutil.rmtree(dir)

    def testUrlChanged(self):
        """testUrlChanged"""
        svn = scm.SvnFetcher()
        svn.fetch('file://%s' % opts['path'], opts['wc'])
        self.assertTrue(os.path.isdir('%s/%s' % (opts['wc'], '.svn')))
        self.assertFalse(
            svn._has_uri_changed(
                'file://%s' % opts['path'],
                opts['wc']
            )
        )
        self.assertTrue(svn._has_uri_changed('hehe_changed', opts['wc']))

    def testRemoveVersionnedDirs(self):
        """testRemoveVersionnedDirs"""
        svn = scm.SvnFetcher()
        svn.fetch('file://%s' % opts['path'], opts['wc'])
        self.assertTrue(os.path.isdir('%s/%s' % (opts['wc'], '.svn')))
        svn._has_uri_changed(opts['wc'], 'file://%s' % opts['path'])
        os.mkdir('%s/%s' % (opts['wc'],'part'))
        svn._remove_versionned_directories(opts['wc'])
        self.assertTrue(os.path.isdir('%s/%s' % (opts['wc'],'part')))
        self.assertFalse(os.path.isfile('%s/%s' % (opts['wc'],'file2')))
        svn.fetch('file://%s' % opts['path'], opts['wc'])
        self.assertTrue(os.path.isdir('%s/%s' % (opts['wc'], '.svn')))

    def testScmInvalidUri(self):
        """testScmInvalidUri"""
        svn = scm.SvnFetcher()
        self.assertRaises(interfaces.InvalidUrlError,
                          svn.fetch, 'invalidsrcuri', 'somewhere')

    def testInvalidReturn(self):
        """testInvalidReturn"""
        svn = scm.SvnFetcher()
        svn.executable = 'notsvn'
        # shell will not find that command, heh
        self.assertRaises(interfaces.FetcherRuntimmeError,
                          svn.fetch, 'file://nowhere', 'somewhere')

        svn = scm.SvnFetcher()
        # prevent mercurial from writing in dest ;)
        os.mkdir(opts['wc'], 660)
        # it will crash luke
        self.assertRaises(interfaces.FetcherRuntimmeError,
                          svn.fetch, 'file://%s' % opts['path'], opts['wc'])
        os.removedirs(opts['wc'])

    def testFetch(self):
        """testFetch"""
        svn = scm.SvnFetcher()
        svn.fetch('file://%s' % opts['path'], opts['wc'])
        self.assertTrue(os.path.isdir('%s/%s' % (opts['wc'], '.svn')))

    def testFetchToParticularRevision(self):
        """testFetchToParticularRevision"""
        svn = scm.SvnFetcher()
        svn.fetch('file://%s' % opts['path'], opts['wc'], dict(revision=1))
        self.assertTrue(os.path.isdir('%s/%s' % (opts['wc'], '.svn')))
        self.assertFalse(os.path.isfile('%s/%s' % (opts['wc'], 'file2')))

    def testUpdate(self):
        """testUpdate"""
        svn = scm.SvnFetcher()
        svn.fetch('file://%s' % opts['path'], opts['wc'], dict(revision=1))
        self.assertTrue(os.path.isdir('%s/%s' % (opts['wc'], '.svn')))
        svn.update('file://%s' % opts['path'], opts['wc'])
        self.assertTrue(os.path.isfile('%s/%s' % (opts['wc'], 'file2')))
        svn.update('file://%s' % opts['path'], opts['wc'], dict(revision=1))
        self.assertFalse(os.path.isfile('%s/%s' % (opts['wc'], 'file2')))

    def testFetchOrUpdate_fetch(self):
        """testFetchOrUpdate_fetch"""
        svn = scm.SvnFetcher()
        svn.fetch_or_update('file://%s' % opts['path'], opts['wc'])
        self.assertTrue(os.path.isfile('%s/%s' % (opts['wc'], 'file2')))
        self.assertTrue(os.path.isdir('%s/%s' % (opts['wc'], '.svn')))

    def testFetchOrUpdate_update(self):
        """testFetchOrUpdate_update"""
        svn = scm.SvnFetcher()
        svn.fetch('file://%s' % opts['path'], opts['wc'], dict(revision=1))
        self.assertTrue(os.path.isdir('%s/%s' % (opts['wc'], '.svn')))
        self.assertFalse(os.path.isfile('%s/%s' % (opts['wc'], 'file2')))
        svn.fetch_or_update('file://%s' % opts['path'], opts['wc'])
        self.assertTrue(os.path.isfile('%s/%s' % (opts['wc'], 'file2')))

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testHg))
    suite.addTest(unittest.makeSuite(testSvn))
    unittest.TextTestRunner(verbosity=2).run(suite)

# vim:set et sts=4 ts=4 tw=80:
