#!/usr/bin/env python

# Copyright (C) 2008, Mathieu PASQUET <kiorky@cryptelium.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

__docformat__ = 'restructuredtext en'

import os
import ConfigParser
import re

from minitage.core import collections

class MinibuildException(Exception):
    """General Minibuild Error."""


class InvalidConfigFileError(MinibuildException):
    """InvalidConfigFileError."""


class NoMinibuildSectionError(MinibuildException):
    """No minibuild section was found in the minibuild."""


class MissingFetchMethodError(MinibuildException):
    """There is no fetch method in the minibuild."""


class MissingCategoryError(MinibuildException):
    """There is no category in the minibuild."""


class InvalidCategoryError(MinibuildException):
    """The category specified is invalid."""


class InvalidFetchMethodError(MinibuildException):
    """The fetch method is invalid."""


class InvalidInstallMethodError(MinibuildException):
    """The install method is invalid."""


class EmptyMinibuildError(MinibuildException):
    """The minibuild is empty."""


class InvalidMinibuildNameError(MinibuildException):
    """The minibuild was not well named."""



class MinilayException(Exception):
    """General Minilay Error."""

class InvalidMinilayPath(MinilayException):
    """The minilay path is invalid."""



""" valid categories to install into"""
VALID_CATEGORIES = ['meta', 'instances', 'eggs', 'dependencies', 'zope', 'django', 'tg']
""" valud install methods to use"""
VALID_INSTALL_METHODS = ['buildout']
"""valid fetch methods to use:
 - hg: mercurial
 - svn: subversion"""
VALID_FETCH_METHODS = ['svn', 'hg']
UNAME = os.uname()[0].lower()

# minibuilds name checkers
# versions _pre1234, _beta1234, _alpha1234, _rc1234, _pre1234
v_sfx = '((pre|p|beta|alpha|rc)\d*)'
# _tagNAME or _branchNAME for scm tags
s_sfx = '((tag|branch)([A-Z]|\d)(\.|[A-Z]|\d)*)'
# _rHEAD or _rTIP or _r1234 -> scm revision
n_sfx = '(r(HEAD|TIP|\d+))'
# major-minor
mn_sfx = '((-\d+((\.\d+)*([a-z]?)))?)'
# complete sufix
sufix = '((%s(_(%s|%s|%s))*)*)' % (mn_sfx, n_sfx, s_sfx, v_sfx)
# packagename : aZ1-az123
m_sfx = '(([a-zA-Z]|\d)+(-([a-zA-Z]|\d)+)*)'
# assemble prefixes
versioned_rxp = '^(%s%s)$' % (m_sfx, sufix)
packageversion_re = re.compile(versioned_rxp)

class Minilay(collections.LazyLoadedDict):
    """Minilays are list of minibuilds.
    they have a special loaded attribute to lazy load them.
    They store minibuilds in a dictionnary:
        -  self[minibuildName][instance] : minibuild instance
        -  self[minibuildName][error] : exception instance if any
    Arguments
        - path: path to the minilay
    """

    def __init__(self, path=None, *kw, **kwargs):
        collections.LazyLoadedDict.__init__(self, *kw, **kwargs)
        self.path = path
        if not os.path.isdir(self.path):
            message = 'This is an invalid directory: \'%s\'' % self.path
            raise InvalidMinilayPath(message)

    def load(self, item=None):
        """Walk the minilay and load everything
        wich seems to be a minibuild inside."""
        if not self.loaded and not item in self.items:
            minibuilds = []
            # 0 is valid
            if item is not None:
                minibuild = '%s/%s' % (self.path, item)
                if os.path.isfile(minibuild):
                    minibuilds.append(item)
            else:
                minibuilds = os.listdir(self.path)
                self.loaded = True
            for minibuild in minibuilds:
                if minibuild not in self.items:
                    self[minibuild] = Minibuild(
                        path='%s/%s' % (self.path,minibuild)
                    )
                    self.items.append(minibuild)

class Minibuild(object):
    """Minibuild object.
    Contains all package metadata including
     - dependenciess
     - url
     - fetch method
     - fetch method options
     - project 's url
     - project 's description
     - install method
    A minibuild has a state
     - False: not ;loaded
     - True:  loaded
    It will read those options in the minibuild section
      - src_uri : url to fetch from
      - src_type : how to fetch (valid methods are 'svn' and 'hg')
      - src_opts : arguments for the fetch method (import, -rxxx) be aware you
        also must include the check out argument if you using SCM fetch method there.
        like co or export. This argument is also not filtered out, take care !
      - depends : which minibuilds we are relying to as prior dependencies
      - url : project's homepage
      - description : a short description
      - install_method : how to install (valid methods are 'buildout')
      """

    def __init__(self, path, *kw, **kwargs):
        """
        Arguments
            path: path to the minibuild file. This minibuild file is pytthon
              configparser like object with a minibuild section which will
              define all the metadate:
        Misc
            Thus we can lazy load minibuilds and save performance.
        """
        self.path = path
        self.name = self.path.split('/').pop()
        self.state = None
        self.dependencies = None
        self.description = None
        self.install_method = None
        self.src_type = None
        self.src_opts = None
        self.src_md5 = None
        self.src_uri = None
        self.url = None
        self.category = None
        self.loaded = None

    def check_minibuild_name(self, name):
        """Check if a minibuild is well named.
        Exceptions:
            - InvalidMinibuildNameError if self.name is not a valid minibuild filename.
        """
        if packageversion_re.match(name):
            return True
        return False

    def __getattribute__(self, attr):
        """Lazyload stuff."""
        lazyloaded = ['config', 'url', 'category', 'src_md5',
                      'dependencies', 'description','src_opts',
                      'src_type', 'install_method', 'src_type']
        if attr in lazyloaded and not self.loaded:
            self.loaded = True
            self.load()
            # case we are always there, setting as loaded
        return object.__getattribute__(self, attr)

    def load(self):
        """Try to load a minibuild.
        Exceptions
            - MinibuildException
        """
        if not self.check_minibuild_name(self.name):
            message = 'Invalid minibuild name : \'%s\'' % self.name
            raise InvalidMinibuildNameError(message)

        try:
            config = ConfigParser.ConfigParser()
            config.read(self.path)
        except Exception,e:
            message = 'The minibuild file format is invalid: %s'
            raise InvalidConfigFileError(message % self.path)

        if not config.has_section('minibuild'):
            message = 'The minibuild %s has no section [minibuild]'
            raise NoMinibuildSectionError(message % self.path)

        # just read the interresting section in the minibuild ;)
        section = config._sections['minibuild']

        # our dependencies, can be empty
        self.dependencies = section.get('depends','').strip().split()
        # specific os dependencies
        os_depends = section.get('depends-%s' % UNAME, None)
        if os_depends:
            self.dependencies.extend(
                [d \
                 for d in os_depends.strip().split()\
                 if d not in self.dependencies]
            )

        # our install method, can be empty
        self.install_method = section.get('install_method','').strip()
        if self.install_method  \
           and not self.install_method in VALID_INSTALL_METHODS:
            messsage = 'The \'%s\' install method is invalid for %s'
            raise InvalidInstallMethodError(
                message % (
                    self.install_method, self.path
                )
            )

        # src_uri is where we will fetch from
        self.src_uri = section.get('src_uri','').strip()
        if self.src_uri:
            # src_type is only important if we have src_uri
            # we just need a src_type is src_uri was specified
            self.src_type = section.get('src_type','').strip()
            if self.src_uri and not self.src_type:
                message = 'You must specify how to fetch your package '
                message += 'into \'%s\' minibuild'
                raise MissingFetchMethodError(message % self.path)
            # src_opts is only important if we have src_uri
            self.src_opts = section.get('src_opts','').strip()
            # src_md5 is only important if we have src_uri
            self.src_md5 = section.get('src_md5','').strip()
            # chech that we got a valid src_type if any
            if not self.src_type in VALID_FETCH_METHODS:
               raise InvalidFetchMethodError(
                   'The \'%s\' src_type is invalid in \'%s\''
                                          % (self.src_type, self.path))
            # if we have a src_uri, we re not a meta package, so we must install
            # somehow, somewhere, so we need a category to install into
            self.category = section.get('category')
            if not self.category:
                message = 'You must specify a category for the \'%s\' minibuild'
                raise MissingCategoryError(message % self.path)
            # check we got a valid category to install into
            if not self.category in VALID_CATEGORIES:
                message = 'the minibuild \'%s\' has an invalid category: %s.\n'
                message += '\tvalid ones are: %s'
                raise InvalidCategoryError(message % (
                    self.path,
                    self.category,
                    VALID_CATEGORIES)
                )

        # misc metadata, optionnal
        self.url = section.get('url','').strip()
        self.description = section.get('description','').strip()

        # but in any case, we must at least have dependencies
        # or a install method
        if not self.install_method and not self.dependencies:
            message = 'There is no install method neither dependencies '
            message += 'for a meta minibuild in \'%s\''
            raise EmptyMinibuildError( message % self.path)

        return self
# vim:set et sts=4 ts=4 tw=80:
