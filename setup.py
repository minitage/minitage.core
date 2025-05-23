import os
import sys
from setuptools import setup, find_packages

name = 'minitage.core'
version = '2.0.58.dev0'
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
    author = 'Makina Corpus',
    author_email = 'freesoftware@makina-corpus.com',
    url = 'http://cheeseshop.python.org/pypi/%s' % name,
    license = 'BSD',
    namespace_packages = [],
    install_requires = ['minitage', 'setuptools'],
    extras_require={'test': ['minitage[test]'],},
    include_package_data = True,
    packages = find_packages('src'),
    package_dir = {'': 'src'},

)

