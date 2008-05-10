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
import os
import sys
import optparse
import ConfigParser

from minitage.core  import api, cli, core

class testConfig(unittest.TestCase):
    """ test cli usage for minimerge"""

    def testConfig(self):
        """testConfig"""
        path = '%s/iamauniqueminiermgeconfigtest' % sys.exec_prefix
        mydict = {'path': path}
        test1 = """
touch %(path)s
cat << EOF > %(path)s
[minimerge]
minilays =
    dir1
    $HOME/test_minimerge1
EOF""" % mydict
        os.system(test1)
        sys.argv = [sys.argv[0], '--config', path, 'bar']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)

        test2 = """
touch %(path)s
cat << EOF > %(path)s
i am not a config file
EOF""" % mydict
        os.system(test2)
        sys.argv = [sys.argv[0], '--config', path, 'bar']
        opts = cli.do_read_options()
        self.assertRaises(core.InvalidConfigFileError, api.Minimerge, opts)
        # cleanup
        os.remove(path)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testConfig))
    unittest.TextTestRunner(verbosity=2).run(suite)

