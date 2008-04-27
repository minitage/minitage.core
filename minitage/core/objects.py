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

from minitage.core import collections
import os
import ConfigParser

class MinibuildException(Exception):pass
class InvalidConfigFileError(MinibuildException): pass
class NoMinibuildSectionError(MinibuildException): pass
class MissingFetchMethodError(MinibuildException): pass
class MissingCategoryError(MinibuildException): pass
class InvalidCategoryError(MinibuildException): pass
class InvalidFetchMethodError(MinibuildException): pass
class EmptyMinibuildError(MinibuildException): pass

''' valid categories to install into'''
VALID_CATEGORIES = ['instances', 'eggs', 'dependencies', 'zope', 'django', 'tg']
''' valud install methods to use'''
VALID_INSTALL_METHODS = ['buildout']
'''valid fetch methods to use:
 - hg: mercurial
 - svn: subversion'''
VALID_FETCH_METHODS = ['svn', 'hg']

class Minilay(collections.LazyLoadedDict):
    '''minilays are list of minibuilds.
    they have a special loaded attribute to lazy load them.
    They store minibuilds in a dictionnary:
        self[minibuildName][instance] -> minibuild instance
        self[minibuildName][error] -> exception instance if any
    :Parameters
    - path: path to the minilay'''

    def __init__(self, path=None, *kw, **kwargs):
        collections.LazyLoadedDict.__init__(self,*kw,**kwargs)
        self.path = path
        self.full_loaded = False

    def load(self, item=None):
        '''walk the minilay and load everything wich seems to be a minibuild inside'''
        if not self.full_loaded:
            minibuilds = []
            if item:
                minibuilds.append(item)
            else:
                minibuilds = os.listdir(self.path)
                self.full_loaded = True
            for minibuild in minibuilds:
                if minibuild not in self.loaded:
                    self[minibuild] = Minibuild(path='%s/%s' % (self.path,minibuild))
                    self.loaded.append(minibuild)

class Minibuild(object):
    '''minibuild object.
    Contains all package metadata including:
        - dependenciess
        - url
        - fetch method
        - project 's url
        - project 's description
        - install method
    A minibuild has a state:
            - False: not ;loaded
            - True:  loaded
            - Exception instance: in error
              Details in the exception

        '''

    def __init__(self, path, *kw, **kwargs):
        '''
        :Parameters:
            - path: path to the minibuild file. This minibuild file is pytthon
            configparser like object with a minibuild section which will define all the metadate:
        :Misc:
            A `loaded` attribute is added to the instance and set to true when attributes will be accessed.
            Thus we can lazy load minibuilds and save performance.
            It will read those options in the minibuild section:
                - src_uri : url to fetch from
                - src_type : how to fetch (valid methods are 'svn' and 'hg')
                - depends : which minibuilds we are relying to as prior dependencies
                - url : project's homepage
                - description : a short description
                - install_method : how to install (valid methods are 'buildout')'''

        self.path = path
        self.name = self.path.split('/').pop()
        self.config = None
        self.loaded = False
        self.config = None
        self.url = None
        self.description = None
        self.install_method = None
        self.src_uri = None
        self.src_type = None
        # lazyloaded attributes
        self.state = None

    def __getattr__(self,attr):
        '''lazyload stuff'''
        if not self.state:
            try:
                self.load()
                # case we are always there, setting as loaded
                self.state = True
            except MinibuildException, e:
                self.state = e
        return self.__dict__.get(attr,None)

    def load(self):
        '''try to load a minibuild
        Throws MinibuildException in error'''
        try:
            self.config = ConfigParser.ConfigParser()
            self.config.read(self.path)
        except:
            raise InvalidConfigFileError('The minibuild file format is invalid: %s' % self.path)

        if not self.config.has_section('minibuild'):
            raise NoMinibuildSectionError('The minibuild %s has no section [minibuild]' % self.path)

        # just read the interresting section in the minibuild ;)
        section = self.config._sections['minibuild']

        # our dependencies, can be empty
        self.dependencies = section.get('depends','').strip().split()
        # our install method, can be empty
        self.install_method = section.get('install_method','').strip().split()

        # src_uri is where we will fetch from
        self.src_uri = section.get('src_uri','').strip()
        # src_type is only important if we have src_uri
        self.src_type = None

        # we just need a src_type is src_uri was specified
        self.src_type = section.get('src_type','').strip()
        if self.src_uri and not self.src_type:
            raise MissingFetchMethodError('You must specify how to fetch your package into \'%s\' minibuild' % self.path)

        # chech that we got a valid src_type if any
        if self.src_type and not self.src_type in VALID_FETCH_METHODS:
            raise InvalidFetchMethodError('The \'%s\' src_uri is invalid in \'%s\'' % (self.src_type, self.path))

        # misc metadata, optionnal
        self.url = section.get('url','').strip()
        self.description = section.get('description','').strip()

        # if we have a src_uri, we are not a meta package, so we must install
        # somehow, somewhere, so we need a category to install into
        self.category = None
        if self.src_uri:
            self.category = section.get('category')
            if not self.category:
                raise MissingCategoryError('You must specify a category for the \'%s\' minibuild' % self.path)
            # check we got a valid category to install into
            if not self.category in VALID_CATEGORIES:
                raise InvalidCategoryError('the minibuild \'%s\' has an invalid category: \'%s\'.\n\tvalid ones are: %s' % (self.path, self.category, VALID_CATEGORIES))

        # but in any case, we must at least have dependencies or a install method
        if not self.install_method and not self.dependencies:
            raise EmptyMinibuildError('There is no install method neither dependencies for a meta minibuild in \'%s\'' % self.path)

        return self
# vim:set et sts=4 ts=4 tw=80:
