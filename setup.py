import os
import sys
from setuptools import setup, find_packages

name = 'minitage.core'
version = '2.0.57.dev0'
def read(rnames):
    setupdir =  os.path.dirname( os.path.abspath(__file__))
    return open(
        os.path.join(setupdir, rnames)
    ).read()

setup(
    name = name,
    version = version,
    description="moved to minitage",
    long_description = (
        read('README.rst')
        + '\n' +
        read('CHANGES.rst')
        + '\n'
    ),
    classifiers=[ ],
    author = 'Mathieu Le Marec - Pasquet',
    author_email = 'kiorky@cryptelium.net',
    url = 'http://cheeseshop.python.org/pypi/%s' % name,
    license = 'BSD',
    namespace_packages = [],
    install_requires = ['minitage'],
    zip_safe = False,
    include_package_data = True,
    packages = find_packages('src'),
    package_dir = {'': 'src'},

)

