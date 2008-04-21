from setuptools import setup, find_packages
import os

version = '0.0.4'
name = 'minitage.core'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name=name,
    version=version,
    description="A meta package-manager to install projects on UNIX Systemes.",
    long_description= (
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
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
    include_package_data=True,
    install_requires = ['zc.buildout', 'setuptools',],
    tests_require = [],
    test_suite = '%s.tests.test_suite' % name,
    entry_points = {},
    zip_safe = False,
)

