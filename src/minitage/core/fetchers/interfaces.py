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



__docformat__ = 'restructuredtext en'

import re
import os
import shutil
import logging

from minitage.core import interfaces
import minitage.core.common

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


class FetcherRuntimeError(IFetcherError):
    """Unknown runtime Error."""

dscms = 'git|hg|bzr|mtn'
p = 'ssh|http|https|ftp|sftp|file'
scms = 'svn|svn\+ssh|cvs'
URI_REGEX = re.compile('^(\/|((%s|%s|%s)(:\/\/)))' % (dscms, p , scms))
__logger__ = 'minitage.interfaces'

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
                'hg': 'minitage.core.fetchers:HgFetcher',
                'bzr': 'minitage.core.fetchers:BzrFetcher',
                'git': 'minitage.core.fetchers:GitFetcher',
                'svn': 'minitage.core.fetchers:SvnFetcher',
                'static': 'minitage.core.fetchers:StaticFetcher',
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
            instance = klass(config = self.sections)
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

    def __init__(self, name, executable = None ,
                 config = None, metadata_directory = None):
        """
        Attributes:
            - name : name of the fetcher
            - executable : path to the executable. Either absolute or local.
            - metadata_directory: optionnal, the metadata directory for the scm
        """
        interfaces.IProduct.__init__(self)
        self.name = name
        self.executable = None
        self.metadata_directory = metadata_directory
        if not config:
            config = {}
        self.config = config
        self.executable = executable
        self._scm_found = None


    def update(self, dest, uri, opts=None, verbose=False):
        """Update a package.
        Exceptions:
            - InvalidUrlError
        Arguments:
            - uri : check out/update uri
            - opts : arguments for the fetcher
            - offline: weither we are offline or online
        """
        raise NotImplementedError('The method is not implemented')

    def fetch(self, dest, uri, ops=None, verbose=False):
        """Fetch a package.
        Exceptions:
            - InvalidUrlError
        Arguments:
            - uri : check out/update uri
            - opts : arguments for the fetcher
            - offline: weither we are offline or online
        """
        raise NotImplementedError('The method is not implemented')

    def fetch_or_update(self, dest, uri, opts = None, verbose=False):
        """Fetch or update a package (call the one of those 2 methods).
        Arguments:
            - uri : check out/update uri
            - opts : arguments for the fetcher
            - offline: weither we are offline or online
            - verbose: set to True to be verbose
        """
        if os.path.isdir(dest):
            if not self.metadata_directory or os.path.isdir(
                os.path.join(dest, self.metadata_directory)):
                self.update(dest, uri, opts, verbose)
            else:
                self.fetch(dest, uri, opts, verbose)
        else:
            self.fetch(dest, uri, opts, verbose)

    def is_valid_src_uri(self, uri):
        """Valid an uri.
        Return:
            boolean if the uri is valid or not
        """
        raise NotImplementedError('The method is not implemented')

    def match(self, switch):
        """Test if the switch match the module."""
        raise NotImplementedError('The method is not implemented')


    def _check_scm_presence(self):
        """check if the scm is in he path"""
        for path in os.environ.get('PATH', '').split(':'):
            exe = os.path.join(path, self.executable)
            if os.path.exists(exe):
                self._scm_found = True
                break

        if not getattr(self, '_scm_found', False):
            message = '%s is not in your path, ' % self.executable
            message += 'please install it or maybe get it into your PATH'
            raise FetcherNotInPathError(message)

    def _scm_cmd(self, command, verbose=False):
        """Helper to run scm commands."""
        self._check_scm_presence()
        logging.getLogger(__logger__).debug(
            'Running %s %s ' % (self.executable, command))
        try:
            minitage.core.common.Popen('%s %s' % (self.executable, command), verbose)
        except Exception, e:
            raise FetcherRuntimeError(e.message)

    def _has_uri_changed(self, dest, uri):
        """Does the uri we fetch from in the working changed or not.
        Arguments
            - dest the working copy
            - uri the uri to fetch from
        Return
            - True if the uri in the working copy changed
        """

        raise NotImplementedError('The method is not implemented')

    def _remove_versionned_directories(self, dest):
        """Remove all directories which contains history.
        part is a special directory, that s where we make install, we will not remove it !
        Arguments
            - dest the working copy
        """
        not_versionned = ['part']
        for filep in os.listdir(dest):
            if not filep in not_versionned:
                path = os.path.join(dest, filep)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)

# vim:set et sts=4 ts=4 tw=80:
