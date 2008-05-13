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
prefix = os.path.abspath(sys.exec_prefix)

os.chdir(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


version = '0.0.4'
name = 'minitage.core'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name=name,
    version=version,
    description="A meta package-manager to install projects on UNIX Systemes.",
    long_description= (
        read('share/minitage/README.txt')
        + '\n' +
        read('share/minitage/CHANGES.txt')
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
    author_email='kiorky@minitage.com',
    url='http://cheeseshop.python.org/pypi/%s' % name,
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['minitage', 'minitage.core'],
    install_requires = ['virtualenv', 'zc.buildout', 'setuptools',],
    tests_require = [],
    test_suite = '%s.tests.test_suite' % name,
    entry_points = {},
    zip_safe = False,
    include_package_data = True,
    package_dir={'etc': 'etc', '/share/minitage':'/share/minitage'},
    data_files = [
        ('%s/etc' % sys.exec_prefix, ['etc/minimerge.cfg']),
        ('%s/share/minitage' % sys.exec_prefix, ['share/minitage/README.txt','share/minitage/CHANGES.txt']),
        ('%s/minilays' % sys.exec_prefix, []),
    ],
    scripts=['bin/minimerge'],
)

# path to setup.py
path = '/'.join(os.path.abspath(__file__).split('/')[:-1])
config = '%s/etc/minimerge.cfg' % path
p_config = os.path.abspath('%s/etc/minimerge.cfg' % prefix)
prefixed = re.sub('%PREFIX%',prefix,open(config,'r').read())
if not os.path.isdir('%s/etc' % prefix):
    os.mkdir('%s/etc' % prefix)


# write default config
open(p_config,'w').write(prefixed)


