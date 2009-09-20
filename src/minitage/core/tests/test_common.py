# Copyright (C) 2009, Mathieu PASQUET <kiorky@cryptelium.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the <ORGANIZATION> nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

__docformat__ = 'restructuredtext en'

import os
import sys
import unittest
from minitage.core.common import first_run

eggs = os.environ.get('MINITAGE_CORE_EGG_PATH', None)
setup = os.environ.get('MINITAGE_CORE_SETUPPY', None)
#if not setup:
#    raise Exception("Please set the 'MINITAGE_CORE_SETUPPY' variable pointing to the setup.py file of the minitage distribution")

def createMinitageEnv(directory):
    """Initialise a minitage in a particular directory."""

    if os.path.exists(os.path.expanduser(directory)):
        raise Exception("Please (re)move %s before test" % directory)
    # faking dev mode
    module =  os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    os.chdir('/')
    os.system("""
              mkdir %(path)s
              cd /
              virtualenv %(path)s --no-site-packages
              source %(path)s/bin/activate
              easy_install virtualenv
              # can be python-ver or python
              $(ls %(path)s/bin/easy_install) -Uf "%(eggs)s" zc.buildout setuptools iniparse
              export PYTHONPATH=%(module)s:$PYTHONPATH
              $(ls %(path)s/bin/python*) -c 'from minitage.core.common import first_run;first_run()'
              """ % {
                  'eggs': eggs,
                  'path': directory,
                  'setup': setup,
                  'module': module,
              }
             )

def write(file, s):
    """Write content to a file."""

    f = open(file,'w')
    f.write(s)
    f.flush()
    f.close()


def bootstrap_buildout(dir):
    """Initialise the bin/buildout file."""

    template = """
##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os, shutil, sys, tempfile, urllib2

tmpeggs = tempfile.mkdtemp()

try:
    import pkg_resources
except ImportError:
    ez = {}
    exec urllib2.urlopen('http://peak.telecommunity.com/dist/ez_setup.py'
                         ).read() in ez
    ez['use_setuptools'](to_dir=tmpeggs, download_delay=0)

    import pkg_resources

cmd = 'from setuptools.command.easy_install import main; main()'
if sys.platform == 'win32':
    cmd = '"%s"' % cmd # work around spawn lamosity on windows

ws = pkg_resources.working_set
assert os.spawnle(
    os.P_WAIT, sys.executable, sys.executable,
    '-c', cmd, '-mqNxd', tmpeggs, 'zc.buildout',
    dict(os.environ,
         PYTHONPATH=
         ws.find(pkg_resources.Requirement.parse('setuptools')).location
         ),
    ) == 0

ws.add_entry(tmpeggs)
ws.require('zc.buildout')
import zc.buildout.buildout
zc.buildout.buildout.main(sys.argv[1:] + ['bootstrap'])
shutil.rmtree(tmpeggs)
"""

    cwd = os.getcwd()
    os.chdir(dir)
    write('bootstrap.py', template)
    os.system('%s bootstrap.py' % sys.executable)
    os.chdir(cwd)


def make_dummy_buildoutdir(ipath):
    os.makedirs(ipath)
    os.chdir(ipath)
    write('buildout.cfg', """
[makers]
[buildout]
options = -c buildout.cfg  -vvvvvv
parts = x
        z
develop = .
[part]
recipe = toto:part
[site-packages-2.4]
recipe = toto:py24
[site-packages-2.5]
recipe = toto:py25
[z]
recipe = toto:luu
[y]
recipe = toto:bar
[x]
recipe = toto """)
    write('setup.py', """
from setuptools import setup
setup(
          name='toto',
          entry_points= {
          'zc.buildout': [
              'default = toto:test',
              'luu = tutu:test',
              'bar = tata:test',
              'py25 = py25:test',
              'py24 = py24:test',
              'part = part:test',
             ]
         }
) """)

    write('toto.py', """
class test:
    def __init__(self,a, b, c):
        pass

    def install(a):
        print "foo" """)
    write('tata.py', """
class test:
    def __init__(self,a, b, c):
        pass

    def install(a):
        open('testbar','w').write('foo') """)
    write('tutu.py', """
class test:
    def __init__(self,a, b, c):
        pass

    def install(a):
        open('testres','w').write('bar') """)

    write('py25.py', """
class test:
    def __init__(self,a, b, c):
        pass

    def install(a):
        open('testres2.5','w').write('2.5') """)

    write('py24.py', """
class test:
    def __init__(self,a, b, c):
        pass

    def install(a):
        open('testres2.4','w').write('2.4') """)
    write('part.py', """
class test:
    def __init__(self,a, b, c):
        pass

    def install(a):
        open('testres','w').write('part') """)
    bootstrap_buildout(ipath)

def test_suite():            
    suite = unittest.TestSuite()
    return suite  


