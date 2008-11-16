# Copyright (C) 2008, 'Mathieu PASQUET <kiorky@cryptelium.net> '
#
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

class LazyLoadedList(list):
    """Just in time objects loading"""

    def __init__(self, *kw, **kwargs):
        list.__init__(self)
        self.loaded = False

    def isLoaded(self):
        """returns True is the minilay has been loaded"""
        return self.loaded

    def load(self):
        """method for lazyloading a list"""
        if not self.isLoaded():
            # do load processing there
            self.loaded = True

    def __getitem__(self, indice):
        """lazy loading items"""
        if not self.isLoaded():
            self.load()
        return list.__getitem__(self, indice)

    def __getslice__(self, start=None, stop=None):
        """lazy loading items"""
        if not self.isLoaded():
            self.load()
        return list.__getslice__(self, start, stop)

    def __contains__(self, item):
        """lazy loading items"""
        if not self.isLoaded():
            self.load()
        return list.__contains__(self, item)

    def index(self, item):
        """lazy loading items"""
        if not self.isLoaded():
            self.load()
        return list.index(self, item)

class LazyLoadedDict(dict):
    """Just in time objects loading"""

    def __init__(self):
        """returns True is the minilay has been loaded"""
        dict.__init__(self)
        self.items = []
        self.loaded = False

    def load(self, item = None):
        """method for lazyloading a list"""
        # do load processing there
        # 3 = 1 + 1
        # marking as loaded
        # 0 is valid
        if item is not None:
            self.items.append(item)
            self.loaded = True

    def __getitem__(self, item):
        """lazy loading items"""
        if not item in self.items:
            self.load(item)
        return dict.__getitem__(self, item)

    def __contains__(self, item):
        """lazy loading items"""
        if not item in self.items:
            self.load(item)
        return dict.__contains__(self, item)

