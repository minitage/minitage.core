__docformat__ = 'restructuredtext en'

import unittest
import tempfile
import os

from minitage.core import common



from minitage.core.tests import base
class TestCommon(base.TestCase):
    """TesMd5."""

    def setUp(self):
        self.path = self.layer['p']
        self.tf = '%s/a'  % self.path

    def testSplitStrip(self):
        """testSplitStrip."""
        self.assertEquals(
            common.splitstrip(' \n666\n2012\n\n\t\n'),
            ['666', '2012']
        )

    def testMd5(self):
        """testMd5."""
        open(self.tf,'w').write('a\n')
        self.assertTrue(
            common.test_md5(
                self.tf,
                '60b725f10c9c85c70d97880dfe8191b3'
            )
        )
        self.assertTrue(
            common.md5sum(self.tf),
            '60b725f10c9c85c70d97880dfe8191b3'
        )
        self.assertFalse(
            common.test_md5(self.tf,
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
        open(self.tf,'w').write('foo')
        self.assertEquals(open(self.tf).read(), 'foo')
        common.substitute(self.tf,'foo','bar')
        self.assertEquals(open(self.tf).read(), 'bar')

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
            common.MinimergeError,
            common.get_from_cache,
            'http://%s' % file,
            download_cache,
            offline = True
        )
        self.assertRaises(
            common.MinimergeError,
            common.get_from_cache,
            'file://%s' % file,
            file_md5 = 'false'
        )

        ret = common.get_from_cache('file://%s' % file,)
        self.assertEquals(open(ret).read(),'foo')
        ret = common.get_from_cache('file://%s' % file,
                                    download_cache = download_cache,)
        self.assertEquals(
            open(ret).read(),
            'foo'
        )
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCommon))
    return suite

