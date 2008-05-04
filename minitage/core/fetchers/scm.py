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
import shutil
import subprocess

from minitage.core.fetchers import interfaces

class InvalidMercurialRepositoryError(interfaces.InvalidRepositoryError): pass

class HgFetcher(interfaces.IFetcher):
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

    def __init__(self):
        interfaces.IFetcher.__init__(self, 'mercurial', 'hg', '.hg')

    def update(self, uri, dest, opts=None, offline = False):
        """update a package
        Parameters:
            - uri : check out/update url
            - dest: destination to fetch to
            - opts : arguments for the fetcher

                - revision: particular revision to deal with.

            - offline: weither we are offline or online
        Exceptions:
            - InvalidMercurialRepositoryError in case of repo problems
            - interfaces.FetchErrorin case of fetch problems
            - interfaces.InvalidUrlError in case of uri is invalid
        """
        if opts is None:
            opts = {}
        revision = opts.get('revision','tip')
        if self.is_valid_src_uri(uri):
            self._scm_cmd('pull -r %s %s -R %s 2>&1' % (revision, uri, dest))
            self._scm_cmd('  up -r %s -R %s 2>&1' % (revision, dest))
            if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
                message = 'Unexpected fetch error on \'%s\'\n' % uri
                message += 'The directory \'%s\' is not a valid mercurial repository' % (dest, uri)
                raise InvalidMercurialRepositoryError(message)
        else:
            raise interfaces.InvalidUrlError('this url \'%s\' is invalid' % uri)

    def fetch(self, uri, dest, opts=None, offline = False):
        """fetch a package
        Parameters:
            - uri : check out/update url
            - dest: destination to fetch to
            - opts : arguments for the fetcher

                - revision: particular revision to deal with.

            - offline: weither we are offline or online
        Exceptions:
            - InvalidMercurialRepositoryError in case of repo problems
            - interfaces.FetchErrorin case of fetch problems
            - interfaces.InvalidUrlError in case of uri is invalid
        """
        if opts is None:
            opts = {}
        revision = opts.get('revision','tip')
        if self.is_valid_src_uri(uri):
            self._scm_cmd('clone -r %s %s %s 2>&1' % (revision, uri,dest))
            if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
                message = 'Unexpected fetch error on \'%s\'\n' % uri
                message += 'The directory \'%s\' is not a valid mercurial repository' % (dest, uri)
                raise InvalidMercurialRepositoryError(message)
        else:
            raise interfaces.InvalidUrlError('this url \'%s\' is invalid' % uri)

    def fetch_or_update(self, uri, dest, opts = None, offline = False):
        """fetch or update a package
        Parameters:
            - uri : check out/update url
            - opts : arguments for the fetcher
            - offline: weither we are offline or online
        """
        if os.path.isdir(dest):
           self.update(uri, dest, opts, offline)
        else:
           self.fetch(uri, dest, opts, offline)

    def is_valid_src_uri(self, uri):
        """Valid an url
        Return:
            boolean if the url is valid or not
        """
        m = interfaces.URI_REGEX.match(uri)
        if m and m.groups()[1] in ['file', 'hg', 'ssh', 'file', 'http', 'https']:
            return True
        return False

    def match(self, switch):
        if switch == 'hg':
            return True
        return False

# vim:set et sts=4 ts=4 tw=80:
