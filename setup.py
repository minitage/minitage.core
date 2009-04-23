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

from setuptools import setup, find_packages

name = 'minitage.core'
version = '1.0'

def read(rnames):
    setupdir =  os.path.dirname( os.path.abspath(__file__))
    return open(
        os.path.join(setupdir, rnames)
    ).read()

setup(
    name = name,
    version = version,
    description="A meta package-manager to deploy projects on UNIX Systemes.",
    long_description = (
        read('README.txt')
        + '\n' +
        read('INSTALL.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n'
    ),
    classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    #keywords = 'development buildout',
    author = 'Mathieu Pasquet',
    author_email = 'kiorky@cryptelium.net',
    url = 'http://cheeseshop.python.org/pypi/%s' % name,
    license = 'GPL',
    namespace_packages = ['minitage', name],
    install_requires = ['virtualenv', 'zc.buildout', 'setuptools>=0.6c9',],
    zip_safe = False,
    include_package_data = True,
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    extras_require={'test': ['IPython', 'zope.testing', 'mocker']},
    data_files = [
        ('etc', ['src/etc/minimerge.cfg']),
        ('minilays', []),
        ('share/minitage', ['README.txt', 'INSTALL.txt', 'CHANGES.txt']),
    ],
    entry_points = {
        'console_scripts': [
            'minimerge = minitage.core.launchers.minimerge:launch',
            'apty = minitage.core.launchers.minimerge:launch',
            'pacmerge = minitage.core.launchers.minimerge:launch',
            'yasty = minitage.core.launchers.minimerge:launch',
        ],
    }

)

