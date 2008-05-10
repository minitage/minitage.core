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

import unittest

from minitage.core.collections import LazyLoadedList, LazyLoadedDict

class testLazyLoadedLists(unittest.TestCase):
    """LazyLoadedList tests."""

    def testLoadedStateChanges(self):
        """Test lazy loading of lazyLoadedLists."""
        lazyLoadedList = LazyLoadedList()
        self.assertFalse(lazyLoadedList.isLoaded())
        lazyLoadedList.append('foo')
        self.assertFalse(lazyLoadedList.isLoaded())
        item = lazyLoadedList[0]
        self.assertTrue(lazyLoadedList.isLoaded())

    def testIn(self):
        """Test insertion in list."""
        lazyLoadedList = LazyLoadedList()
        self.assertFalse(lazyLoadedList.isLoaded())
        self.assertFalse('foo' in lazyLoadedList)
        lazyLoadedList.append('foo')
        self.assertTrue('foo' in lazyLoadedList)
        self.assertTrue(lazyLoadedList.isLoaded())

    def testAdd(self):
        """Test append on list."""
        lazyLoadedList = LazyLoadedList()
        self.assertFalse(lazyLoadedList.isLoaded())
        lazyLoadedList.append(0)
        self.assertTrue(0 == lazyLoadedList.index(0))
        self.assertTrue(lazyLoadedList.isLoaded())

    def testSlices(self):
        """Test sub slices of list."""
        lazyLoadedList = LazyLoadedList()
        self.assertFalse(lazyLoadedList.isLoaded())
        for i in range(5):
            lazyLoadedList.append(i)
        self.assertFalse(lazyLoadedList.isLoaded())
        ta = lazyLoadedList[:2]
        tb = lazyLoadedList[4:]
        tc = lazyLoadedList[:]
        self.assertTrue(lazyLoadedList.isLoaded())
        self.assertTrue([0, 1] == ta)
        self.assertTrue([0, 1, 2, 3, 4] == tc)
        self.assertTrue([4] == tb)


class testLazyLoadedDicts(unittest.TestCase):
    """LazyLoadedDict tests."""

    def testLoadedStateChanges(self):
        """Test lazy loading of lazyLoadedDict."""
        lazyLoadedDict = LazyLoadedDict()
        self.assertFalse(0 in lazyLoadedDict.items)
        lazyLoadedDict[0] = 'foo'
        self.assertFalse(0 in lazyLoadedDict.items)
        item = lazyLoadedDict[0]
        self.assertTrue(0 in lazyLoadedDict.items)

    def testIn(self):
        """Test in operator in dictonary."""
        lazyLoadedDict = LazyLoadedDict()
        self.assertFalse('foo' in lazyLoadedDict.items)
        self.assertFalse('foo' in [key for key in lazyLoadedDict])
        lazyLoadedDict['foo'] = 'foo'
        self.assertTrue('foo' in [key for key in lazyLoadedDict])
        self.assertFalse('foo' in lazyLoadedDict.items)
        a = lazyLoadedDict['foo']
        self.assertTrue(a and 'foo' in lazyLoadedDict.items)

    def testNotIn(self):
        """Test non-appartenance of an element in the dictonary."""
        lazyLoadedDict = LazyLoadedDict()
        self.assertFalse('foo' in lazyLoadedDict.items)
        self.assertTrue('foo'  not in lazyLoadedDict.items)
        self.assertFalse('foo' in [key for key in lazyLoadedDict])
        lazyLoadedDict['foo'] = 'foo'
        self.assertTrue('foo' in [key for key in lazyLoadedDict])
        self.assertFalse('foo' in lazyLoadedDict.items)
        a = lazyLoadedDict['foo']
        self.assertTrue(a and 'afoo' not in lazyLoadedDict.items)

    def testAdd(self):
        """Test addition of an element in the dictonary."""
        lazyLoadedDict = LazyLoadedDict()
        self.assertFalse(0 in lazyLoadedDict.items)
        lazyLoadedDict[0] = 0
        keys = [key for key in lazyLoadedDict]
        self.assertTrue(lazyLoadedDict.has_key(0))
        item = lazyLoadedDict[0]
        self.assertTrue(len(lazyLoadedDict.items) == 1)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testLazyLoadedLists))
    suite.addTest(unittest.makeSuite(testLazyLoadedDicts))
    unittest.TextTestRunner(verbosity=2).run(suite)

