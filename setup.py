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

# workaround to get version
__version__ = '0.0.4'
if os.path.isdir("src"):
    sys.path.append("src")
from minitage.core.core import __version__

name = 'minitage.core'

prefix = os.path.abspath(sys.exec_prefix)
setupdir =  os.path.dirname(
    os.path.abspath(__file__)
)

def read(rnames):
    return open(
        os.path.join(setupdir, rnames)
    ).read()

setup(
    name=name,
    version=__version__,
    description="A meta package-manager to install projects on UNIX Systemes.",
    long_description= (
        read('src/share/minitage/README.txt')
        + '\n' +
        read('src/share/minitage/INSTALL.txt')
        + '\n' +
        read('src/share/minitage/CHANGES.txt')
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
    #namespace_packages=['minitage', name],
    install_requires = ['virtualenv',
                        'zc.buildout',
                        'setuptools',],
    tests_require = [],
    test_suite = '%s.tests.test_suite' % name,
    zip_safe = False,
    packages=find_packages('src'),
    package_dir={'src/etc': 'etc', 'src/share/minitage': 'share/minitage', '': 'src'},
    extras_require={'test': ['IPython', 'zope.testing', 'mocker']},
    #data_files = [
    #    ('etc', ['etc/minimerge.cfg']),
    #    ('share/minitage'  , ['share/minitage/README.txt']),
    #    ('share/minitage' , ['share/minitage/CHANGES.txt']),
    #    ('minilays', []),
    #],
    include_package_data = True,
    entry_points = {
        'console_scripts': [
            'minimerge = minitage.core.launchers.minimerge:launch',
        ],
    }

)

