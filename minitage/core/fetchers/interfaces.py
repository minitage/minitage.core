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

import re
import os
import subprocess
import shutil

from minitage.core import interfaces

class IFetcherError(Exception):
    """General Fetcher Error."""


class InvalidUrlError(IFetcherError):
    """Invalid url."""


class UpdateError(IFetcherError):
    """Update Error."""


class FetchError(IFetcherError):
    """Fetch Error."""


class InvalidRepositoryError(IFetcherError):
    """Repository is invalid."""


class FetcherNotInPathError(IFetcherError):
    """Fetcher was not found."""


class FetcherRuntimmeError(IFetcherError):
    """Unknown runtime Error."""



dscms = 'git|hg|bzt|mtn'
p = 'ssh|http|https|ftp|sftp|file'
scms = 'svn|svn\+ssh|cvs'
URI_REGEX = re.compile('^((%s|%s|%s):\/\/(.*))$' % (dscms, p , scms))

class IFetcherFactory(interfaces.IFactory):
    """Interface Factory."""

    def __init__(self, config=None):
        """
        Arguments:
            - config: a configuration file with a self.name section
                    containing all needed classes.
        """

        interfaces.IFactory.__init__(self, 'fetchers', config)
        self.registerDict(
            {
                'hg': 'minitage.core.fetchers.scm.HgFetcher',
                'svn': 'minitage.core.fetchers.scm.SvnFetcher',
            }
        )

    def __call__(self, switch):
        """return a fetcher
        Arguments:
            - switch: fetcher type
              Default ones:

                -hg: mercurial
                -svn: subversion
        """
        for key in self.products:
            klass = self.products[key]
            instance = klass(config = self.section)
            if instance.match(switch):
                return instance

class IFetcher(interfaces.IProduct):
    """Interface for fetching a package from somewhere.
    Basics
         To register a new fetcher to the factory you ll have 2 choices:
             - Indicate something in a config.ini file and give it to the
               instance initialization.
               Example::
                   [fetchers]
                   type=mymodule.mysubmodule.MyFetcherClass

             - register it manually with the .. function::register
               Example::
                   >>> klass = getattr(module,'superklass')
                   >>> factory.register('svn', klass)
    What a fetcher needs to be a fetcher
        Locally, the methods in the interfaces ;)
        Basically, it must implement
            - fetch, update, fetch_or_update to get the source
            - is_valid_src_uri to know if the src url is good
            - _remove_versionned_directories to remove the metadatas from the
              previous co
            - _has_uri_changed to know if we get the source from the last repo
              we got from or a new one.
    """

    def __init__(self, name, executable,
                 config = None, metadata_directory = None):
        """
        Attributes:
            - name : name of the fetcher
            - executable : path to the executable. Either absolute or local.
            - metadata_directory: optionnal, the metadata directory for the scm
        """
        self.name = name
        self.executable = None
        self.metadata_directory = metadata_directory
        if not config:
            config = {}
        self.config = config
        if executable is None:
            executable = ''
        if not '/' in executable:
            for path in os.environ['PATH'].split(os.pathsep):
                if os.path.isfile('%s/%s' % (path, executable)):
                    self.executable = '%s/%s' % (path, executable)
                    break
        else:
            if os.path.isfile(executable):
                self.executable = executable

        if self.executable is None:
            message = '%s is not in your path, please install it or '
            message += 'maybe get it into your PATH' % self.executable
            raise FetcherNotInPathError(message)

    def update(self, uri, dest, opts=None):
        """Update a package.
        Exceptions:
            - InvalidUrlError
        Arguments:
            - uri : check out/update uri
            - opts : arguments for the fetcher
            - offline: weither we are offline or online
        """
        raise interfaces.NotImplementedError('The method is not implemented')

    def fetch(self, uri, dest, ops=None):
        """Fetch a package.
        Exceptions:
            - InvalidUrlError
        Arguments:
            - uri : check out/update uri
            - opts : arguments for the fetcher
            - offline: weither we are offline or online
        """
        raise interfaces.NotImplementedError('The method is not implemented')

    def fetch_or_update(self, uri, dest, opts = None):
        """Fetch or update a package (call the one of those 2 methods).
        Arguments:
            - uri : check out/update uri
            - opts : arguments for the fetcher
            - offline: weither we are offline or online
        """
        raise interfaces.NotImplementedError('The method is not implemented')

    def is_valid_src_uri(self, uri):
        """Valid an uri.
        Return:
            boolean if the uri is valid or not
        """
        raise interfaces.NotImplementedError('The method is not implemented')

    def match(self, switch):
        """Test if the switch match the module."""
        raise interfaces.NotImplementedError('The method is not implemented')

    def _scm_cmd(self, command):
        """Helper to run scm commands."""
        p = subprocess.Popen('%s %s 2>&1' % (self.executable, command),
                             shell = True, stdout=subprocess.PIPE)
        ret = p.wait()
        if ret != 0:
            message = '%s failed to achieve correctly.' % self.name
            raise FetcherRuntimmeError(message)

    def _has_uri_changed(self, uri, dest):
        """Does the uri we fetch from in the working changed or not.
        Arguments
            - dest the working copy
            - uri the uri to fetch from
        Return
            - True if the uri in the working copy changed
        """

        raise interfaces.NotImplementedError('The method is not implemented')

    def _remove_versionned_directories(self, dest):
        """Remove all directories which contains history.
        part is a special directory, that s where we make install, we will not remove it !
        Arguments
            - dest the working copy
        """
        not_versionned = ['part']
        for file in os.listdir(dest):
            if not file in not_versionned:
                path = '%s/%s' % (dest, file)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)

# vim:set et sts=4 ts=4 tw=80:
