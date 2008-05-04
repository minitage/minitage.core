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

from minitage.core import interfaces

class IFetcherError(Exception): pass
class InvalidUrlError(IFetcherError): pass
class UpdateError(IFetcherError): pass
class FetchError(IFetcherError): pass
class InvalidRepositoryError(IFetcherError): pass
class FetcherNotInPathError(IFetcherError): pass
class FetcherRuntimmeError(IFetcherError): pass

URI_REGEX = re.compile('^((svn\+ssh|git|http|https|hg|svn|ftp|sftp|ssh|bzr|cvs|mtn|file):\/\/(.*))$')

class IFetcher(interfaces.IProduct):
    """Interface for fetching a package from somewhere"
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
    """

    def __init__(self, name, executable, metadata_directory = None):
        """
        Attributes:
            - name : name of the fetcher
            - executable : path to the executable. Either absolute or local.
            - metadata_directory: optionnal, the metadata directory for the scm
        """
        self.name = name
        self.executable = None
        self.metadata_directory = metadata_directory
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
            message = '%s is not in your path, please install it or maybe get it into your PATH' % self.executable
            raise FetcherNotInPathError(message)

    def update(self, uri, dest, opts=None, offline = False):
        """update a package
        Exceptions:
            - InvalidUrlError
        Parameters:
            - uri : check out/update url
            - opts : arguments for the fetcher
            - offline: weither we are offline or online
        """
        raise interfaces.NotImplementedMethodError('The method is not implemented')

    def fetch(self, uri, dest, ops=None, offline = False):
        """fetch a package
        Exceptions:
            - InvalidUrlError
        Parameters:
            - uri : check out/update url
            - opts : arguments for the fetcher
            - offline: weither we are offline or online
        """
        raise interfaces.NotImplementedMethodError('The method is not implemented')

    def fetch_or_update(self, uri, dest, opts = None, offline = False):
        """fetch or update a package (call the one of those 2 methods)
        Parameters:
            - uri : check out/update url
            - opts : arguments for the fetcher
            - offline: weither we are offline or online
        """
        raise interfaces.NotImplementedMethodError('The method is not implemented')

    def is_valid_src_uri(self, uri):
        """Valid an url
        Return:
            boolean if the url is valid or not
        """
        raise interfaces.NotImplementedMethodError('The method is not implemented')

    def match(self, switch):
        raise interfaces.NotImplementedMethodError('The method is not implemented')

    def _scm_cmd(self, command):
        """helper to run scm commands"""
        p = subprocess.Popen('%s %s 2>&1' % (self.executable, command), shell = True, stdout=subprocess.PIPE)
        ret = p.wait()
        if ret != 0:
            raise FetcherRuntimmeError('%s failed to achieve correctly.' % self.name)

# vim:set et sts=4 ts=4 tw=80:
