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
from minitage.core import interfaces, fetchers
from minitage.core.fetchers import scm

class testInterfaces(unittest.TestCase):
    """testInterfaces"""

    def testIFetcher(self):
        """testIFetcher"""
        i = fetchers.interfaces.IFetcher('ls', 'ls')
        self.assertRaises(NotImplementedError,
                          i.update, 'foo', 'bar')
        self.assertRaises(NotImplementedError,
                          i.fetch_or_update, 'foo', 'bar')
        self.assertRaises(NotImplementedError,
                          i.fetch, 'foo', 'bar')
        self.assertRaises(NotImplementedError,
                          i.is_valid_src_uri, 'foo')
        self.assertRaises(NotImplementedError,
                          i.match, 'foo')
        self.assertRaises(NotImplementedError,
                          i._has_uri_changed, 'foo', 'bar')

    def testURI(self):
        """testURI"""
        re = fetchers.interfaces.URI_REGEX
        self.assertEquals(re.match('http://tld').groups()[1], 'http')
        self.assertEquals(re.match('mtn://tld').groups()[1], 'mtn')
        self.assertEquals(re.match('svn://tld').groups()[1], 'svn')
        self.assertEquals(re.match('cvs://tld').groups()[1], 'cvs')
        self.assertEquals(re.match('bzr://tld').groups()[1], 'bzr')
        self.assertEquals(re.match('https://tld').groups()[1], 'https')
        self.assertEquals(re.match('ftp://tld').groups()[1], 'ftp')
        self.assertEquals(re.match('hg://tld').groups()[1], 'hg')
        self.assertEquals(re.match('git://tld').groups()[1], 'git')
        self.assertEquals(re.match('ssh://tld').groups()[1], 'ssh')
        self.assertEquals(re.match('sftp://tld').groups()[1], 'sftp')
        self.assertEquals(re.match('file://tld').groups()[1], 'file')
        self.assertEquals(re.match('svn+ssh://tld').groups()[1], 'svn+ssh')

    def testInit(self):
        """testInit"""
        f = fetchers.interfaces.IFetcher('ls', 'ls', metadata_directory='.ls')
        self.assertEquals(f.name,'ls')
        self.assertEquals(f.executable,'/bin/ls')
        self.assertEquals(f.metadata_directory,'.ls')
        f = fetchers.interfaces.IFetcher('ls','/bin/ls')
        self.assertEquals(f.executable,'/bin/ls')
        self.assertRaises(fetchers.interfaces.FetcherNotInPathError,
                          fetchers.interfaces.IFetcher, 'ls','/bin/notfoundheh')

    def testFactory(self):
        """testFactory"""
        f = fetchers.interfaces.IFetcherFactory()
        svn = f('svn')
        hg = f('hg')
        self.assertEquals(hg.__class__.__name__,
                          fetchers.scm.HgFetcher.__name__)
        self.assertEquals(svn.__class__.__name__,
                          fetchers.scm.SvnFetcher.__name__)
        self.assertEquals(svn.__module__,
                          fetchers.scm.SvnFetcher.__module__)
        self.assertEquals(hg.__module__,
                          fetchers.scm.HgFetcher.__module__)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testInterfaces))
    unittest.TextTestRunner(verbosity=2).run(suite)

# vim:set et sts=4 ts=4 tw=80:
