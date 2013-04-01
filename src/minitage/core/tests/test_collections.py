__docformat__ = 'restructuredtext en'

import unittest

from minitage.core.tests.base import TestCase
from minitage.core.collections import LazyLoadedList, LazyLoadedDict

class testLazyLoadedLists(TestCase):
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


class testLazyLoadedDicts(TestCase):
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

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testLazyLoadedLists))
    suite.addTest(unittest.makeSuite(testLazyLoadedDicts))
    return suite
