# Copyright (C)2008, 'Mathieu PASQUET <kiorky@cryptelium.net> '
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
import os
import sys
import re

from setuptools import setup, find_packages
from minitage.core.core import __version__

prefix = os.path.abspath(sys.exec_prefix)
setupdir =  os.path.dirname(
    os.path.abspath(__file__)
)

os.chdir(setupdir)
name = 'minitage.core'

def read(rnames):
    return open(
        os.path.join(setupdir, rnames)
    ).read()

setup(
    name=name,
    version=__version__,
    description="A meta package-manager to install projects on UNIX Systemes.",
    long_description= (
        read('share/minitage/README.txt')
        + '\n' +
        read('share/minitage/INSTALL.txt')
        + '\n' +
        read('share/minitage/CHANGES.txt')
        + '\n' 
    ),
    classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='development buildout',
    author='Mathieu Pasquet',
    author_email='kiorky@cryptelium.net',
    url='http://cheeseshop.python.org/pypi/%s' % name,
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['minitage', name],
    install_requires = ['virtualenv', 
                        'zc.buildout', 
                        'setuptools',],
    tests_require = [],
    test_suite = '%s.tests.test_suite' % name,
    zip_safe = False,
    include_package_data = True,
    package_dir={'etc': 'etc', 'share/minitage': 'share/minitage',},
    data_files = [
        ('etc', ['etc/minimerge.cfg']),
        ('share/minitage'  , ['share/minitage/README.txt']),
        ('share/minitage' , ['share/minitage/CHANGES.txt']),
        ('minilays', []),
    ],
    entry_points = {
        'console_scripts': [
            'minimerge = minitage.core.launchers.minimerge:launch',
        ],
    }

)

## path to setup.py
#config = os.path.join(
#    setupdir, 'etc', 'minimerge.cfg'
#)
#p_config = os.path.abspath('%s/etc/minimerge.cfg' % prefix)
#prefixed = re.sub('%PREFIX%',prefix,open(config,'r').read())
#if not os.path.isdir('%s/etc' % prefix):
#    os.mkdir('%s/etc' % prefix)
## write default config
#open(p_config,'w').write(prefixed)

