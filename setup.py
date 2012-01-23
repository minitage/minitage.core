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



import os
import sys

from setuptools import setup, find_packages

name = 'minitage.core'
version = '2.0.28'
def read(rnames):
    setupdir =  os.path.dirname( os.path.abspath(__file__))
    return open(
        os.path.join(setupdir, rnames)
    ).read()

setup(
    name = name,
    version = version,
    description="A meta package-manager to deploy projects on UNIX Systemes sponsored by Makina Corpus.",
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
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    #keywords = 'development buildout',
    author = 'Mathieu Pasquet',
    author_email = 'kiorky@cryptelium.net',
    url = 'http://cheeseshop.python.org/pypi/%s' % name,
    license = 'BSD',
    namespace_packages = ['minitage', name],
    install_requires = ['iniparse', 'zc.buildout', 'minitage.paste >= 1.3.1850', 'ordereddict'],
    zip_safe = False,
    include_package_data = True,
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    extras_require={'test': ['IPython', 'zope.testing', 'mocker', 'httplib2']},
    data_files = [
        ('etc', ['src/etc/minimerge.cfg']),
        ('minilays', []),
        ('share/minitage', ['README.txt', 'INSTALL.txt', 'CHANGES.txt']),
    ],
    entry_points = {
        'console_scripts': [
            'minimerge = minitage.core.launchers.minimerge:launch',
        ],
    }

)



