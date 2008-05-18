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
import tempfile
import os

from minitage.core import common, core

path = tempfile.mkdtemp('minitagetestcomon')
tf = '%s/a'  % path

class TestCommon(unittest.TestCase):
    """TesMd5."""

    def testMd5(self):
        """testMd5."""
        open(tf,'w').write('a\n')
        self.assertTrue(
            common.test_md5(
                tf,
                '60b725f10c9c85c70d97880dfe8191b3'
            )
        )
        self.assertTrue(
            common.md5sum(tf),
            '60b725f10c9c85c70d97880dfe8191b3'
        )
        self.assertFalse(
            common.test_md5(tf,
                            'FALSE'
                           )
        )

    def testRemovePath(self):
        """testRemovePath."""
        file = tempfile.mkstemp()
        file = file[1]
        open(file,'w').write('a')
        self.assertTrue(os.path.isfile(file))
        common.remove_path(file)
        self.assertFalse(os.path.isfile(file))

        a = tempfile.mkdtemp()
        self.assertTrue(os.path.isdir(a))
        common.remove_path(a)
        self.assertFalse(os.path.isdir(a))

    def testAppendVar(self):
        """testAppendVar."""
        os.environ['TEST'] = 'test'
        self.assertEquals(os.environ['TEST'], 'test')
        common.append_env_var('TEST', ["toto"], sep='|', before=False)
        self.assertEquals(os.environ['TEST'], 'test|toto')
        common.append_env_var('TEST', ["toto"], sep='|', before=True)
        self.assertEquals(os.environ['TEST'], 'toto|test|toto')

    def testSubstitute(self):
        """testSubstitute."""
        open(tf,'w').write('foo')
        self.assertEquals(open(tf).read(), 'foo')
        common.substitute(tf,'foo','bar')
        self.assertEquals(open(tf).read(), 'bar')

    def testSystem(self):
        """testSystem."""
        self.assertRaises(SystemError, common.system, '6666')

    def testGetFromCache(self):
        """testGetFromCache."""
        ret, file = tempfile.mkstemp()
        filename = 'myfilename'
        download_cache = tempfile.mkdtemp()
        open(file, 'w').write('foo')
        self.assertRaises(
            core.MinimergeError,
            common.get_from_cache,
            'file://%s' % file,
            filename,
            offline = True
        )
        self.assertRaises(
            core.MinimergeError,
            common.get_from_cache,
            'file://%s' % file,
            md5 = 'false'
        )

        ret = common.get_from_cache('file://%s' % file,)
        self.assertEquals(open(ret).read(),'foo')
        ret = common.get_from_cache('file://%s' % file,
                                    download_cache = download_cache,)
        self.assertEquals(
            open(ret).read(),
            'foo'
        )

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCommon))
    unittest.TextTestRunner(verbosity=2).run(suite)



# vim:set et sts=4 ts=4 tw=80:
