# Copyright (C) 2008, 'Mathieu PASQUET <kiorky@cryptelium.net>'
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

__docformat__ = 'restructuredtext en'

import ConfigParser
import optparse
import os
import shutil
import sys
import unittest
import test_common
from minitage.core import api, objects

mb_path = os.path.expanduser('~/iamatest-1.0')

class testMinibuilds(unittest.TestCase):
    """ test cli usage for minimerge"""

    def testValidNames(self):
        mb = api.Minibuild(path=mb_path)
        valid_names = []
        valid_names.append('test-1.0')
        valid_names.append('test-test-1.0')
        valid_names.append('test-1.0.3')
        valid_names.append('test-1.0_beta444')
        valid_names.append('test-1.0_beta444_pre20071024')
        valid_names.append('test-1.0_alpha44')
        valid_names.append('test-1.0_alpha44_pre20071024')
        valid_names.append('test-1.0_pre20071024')
        valid_names.append('meta-toto')
        for i in valid_names:
            # will fail if raise error anyway
            self.assertTrue(mb.check_minibuild_name(i))
        invalid_names = []
        invalid_names.append('test')
        invalid_names.append('test-')
        invalid_names.append('test-1.0_prout4')
        invalid_names.append('test_prout4-1.0')
        invalid_names.append('test-test')
        invalid_names.append('test-test-')
        invalid_names.append('meta')
        invalid_names.append('meta-meta-')
        invalid_names.append('meta-')
        for i in invalid_names:
            # will fail if raise error anyway
            self.assertFalse(mb.check_minibuild_name(i))
        minibuild1="""
        [minibuild]
        depends=python
        src_type=hg
        src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
        install_method=buildout
        category=eggs
        """
        nvmbp = 'notvalidminibuildnamewhichisuniquetothistestforminitage'
        open(nvmbp,'w').write(minibuild1)
        mb = api.Minibuild(path=nvmbp)
        self.assertRaises(objects.InvalidMinibuildNameError,mb.load)
        os.remove(nvmbp)

    def testDepends(self):
        minibuild1="""
[minibuild]
depends=python
src_type=hg
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
install_method=buildout
category=eggs
"""
        open(mb_path,'w').write(minibuild1)
        mb = api.Minibuild(path=mb_path).load()
        self.assertEquals(mb.dependencies, ['python'])

    def testValidMinibuilds(self):
        minibuild1="""
[minibuild]
depends=python
src_type=hg
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
install_method=buildout
category=eggs
"""
        open(mb_path,'w').write(minibuild1)
        mb = api.Minibuild(path=mb_path).load()

    def testNoMinibuildSection(self):
        minibuild2="""
[iamnotcalledminibuild]
depends=python
src_type=hg
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
install_method=buildout
category=eggs
"""
        open(mb_path,'w').write(minibuild2)
        mb = api.Minibuild(path=mb_path)
        self.assertRaises(objects.NoMinibuildSectionError, mb.load)

    def testInvalidConfig(self):
        minibuild3="""
depends=python
src_type=hg
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
install_method=buildout
category=eggs
"""
        open(mb_path,'w').write(minibuild3)
        mb = api.Minibuild(path=mb_path)
        self.assertRaises(objects.InvalidConfigFileError, mb.load)

    def testUriWithoutFetchMethod(self):
        minibuild="""
[minibuild]
category=eggs
depends=python
install_method=buildout
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
"""
        open(mb_path,'w').write(minibuild)
        mb = api.Minibuild(path=mb_path)
        self.assertRaises(objects.MissingFetchMethodError, mb.load)

    def testInvalidSrcType(self):
        minibuild="""
[minibuild]
category=eggs
depends=python
install_method=buildout
src_type=invalid
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
"""
        open(mb_path,'w').write(minibuild)
        mb = api.Minibuild(path=mb_path)
        self.assertRaises(objects.InvalidFetchMethodError, mb.load)
    def testSrcOpts(self):
        minibuild="""
[minibuild]
category=eggs
depends=python
install_method=buildout
src_type=invalid
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_opts=-r666
"""
        open(mb_path,'w').write(minibuild)
        mb = api.Minibuild(path=mb_path)
        self.assertEquals('-r666',mb.src_opts)

    def testMeta(self):
        minibuild="""
[minibuild]
depends=python
"""
        open(mb_path,'w').write(minibuild)
        # no tests there, if it has errors in loading, it will fail anyway...
        mb = api.Minibuild(path=mb_path).load()
        self.failUnless('python' in mb.dependencies)

    def testDefaults(self):
        minibuild="""
[minibuild]
depends=python
"""
        open(mb_path,'w').write(minibuild)
        mb = api.Minibuild(path=mb_path).load()

    def testCategory(self):
        minibuild="""
[minibuild]
depends=python
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
"""
        open(mb_path,'w').write(minibuild)
        mb = api.Minibuild(path=mb_path).load()
        self.assertEquals(mb.category,'eggs')

        minibuild="""
[minibuild]
depends=python
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=invalid
"""
        mb = None
        open(mb_path,'w').write(minibuild)
        mb = api.Minibuild(path=mb_path)
        self.assertRaises(objects.InvalidCategoryError, mb.load)
        minibuild="""
[minibuild]
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
"""
        mb = None
        open(mb_path,'w').write(minibuild)
        mb = api.Minibuild(path=mb_path)
        self.assertRaises(objects.MissingCategoryError, mb.load)

    def testMinibuildWithoutInstallMethodNeitherDependencies(self):
        minibuild="""
[minibuild]
url=prout
"""
        open(mb_path,'w').write(minibuild)
        mb = api.Minibuild(path=mb_path)
        self.assertRaises(objects.EmptyMinibuildError, mb.load)


    def testLazyLoad(self):
        minibuild="""
[minibuild]
depends=python
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
"""
        # minibuild is ok, just trying to get the catgory.
        open(mb_path,'w').write(minibuild)
        mb = api.Minibuild(path=mb_path)
        self.assertEquals(mb.category,'eggs')

        minibuild="""
[minibuild]
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=eggs
"""
        # minibuild is ok, just trying to get the catgory.
        open(mb_path,'w').write(minibuild)
        mbd = api.Minibuild(path=mb_path)
        self.assertEquals(mbd.dependencies,[])

        minibuild="""
[minibuild]
depends=python
src_uri=https://hg.minitage.org/minitage/buildouts/ultimate-eggs/elementtreewriter-1.0/
src_type=hg
install_method=buildout
category=invalid
"""
        mb = None
        open(mb_path,'w').write(minibuild)
        mb = api.Minibuild(path=mb_path)
        categ = mb.category
        self.assertTrue( isinstance(mb.loaded, objects.MinibuildException))

    def tearDown(self):
        os.remove(mb_path)

    def setUp(self):
        open(mb_path,'w').write('')

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testMinibuilds))
    unittest.TextTestRunner(verbosity=2).run(suite)

