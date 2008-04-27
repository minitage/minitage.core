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

import os

if os.environ.get('MINITAGE_CORE_EGG_PATH',None):
    setup = os.environ.get('MINITAGE_CORE_EGG_PATH')
else:
    raise Exception("Please set the 'MINITAGE_CORE_EGG_PATH' variable pointing to the setup.py file of the minitage distribution")

def createMinitageEnv(dir):
    if os.path.exists(os.path.expanduser(dir)):
        raise Exception("Please (re)move %s before test" % dir)
    os.system('''
              mkdir %(path)s
              virtualenv %(path)s
              source %(path)s/bin/activate
              # can be python-ver or python
              $(ls %(path)s/bin/python*) %(setup)s install
              ''' % {
                  'setup': setup,
                  'path': dir,
              }
             )



