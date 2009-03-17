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
from makers import (test_interfaces,
                    test_buildout,
                   )
def test_suite():
    suite = unittest.TestSuite()
    for m in (test_interfaces,
              test_buildout,
             ):
        suite.addTest(m.test_suite())
    suite = unittest.TestSuite()
    return suite
# vim:set et sts=4 ts=4 tw=80:
