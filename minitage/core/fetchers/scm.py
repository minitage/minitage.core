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
import re

from minitage.core.fetchers import interfaces

class InvalidMercurialRepositoryError(interfaces.InvalidRepositoryError): pass
class OfflineModeRestrictionError(interfaces.IFetcherError): pass

class HgFetcher(interfaces.IFetcher):
    """ Mercurial Fetcher
    Example::
        >>> import minitage.core.fetchers.scm
        >>> hg = scm.HgFetcher()
        >>> hg.fetch_or_update('http://uri','/dir',{revision='tip'})
    """

    def __init__(self, config = None):
        if not config:
            config = None
        interfaces.IFetcher.__init__(self, 'mercurial', 'hg', config, '.hg')

    def update(self, uri, dest, opts=None):
        """update a package
        Arguments:
            - uri : check out/update uri
            - dest: destination to fetch to
            - opts : arguments for the fetcher

                - revision: particular revision to deal with.

        Exceptions:
            - InvalidMercurialRepositoryError in case of repo problems
            - interfaces.FetchErrorin case of fetch problems
            - interfaces.InvalidUrlError in case of uri is invalid
        """
        if opts is None:
            opts = {}
        revision = opts.get('revision','tip')
        if self.is_valid_src_uri(uri):
            if self._has_uri_changed(uri, dest):
                self._remove_versionned_directories(dest)
                self._scm_cmd('init %s' % (dest))
                if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
                    message = 'Unexpected fetch error on \'%s\'\n' % uri
                    message += 'The directory \'%s\' is not a valid mercurial repository' % (dest)
                    raise InvalidMercurialRepositoryError(message)
            self._scm_cmd('pull -f -r %s %s -R %s' % (revision, uri, dest))
            self._scm_cmd('  up -r %s -R %s ' % (revision, dest))
            if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
                message = 'Unexpected fetch error on \'%s\'\n' % uri
                message += 'The directory \'%s\' is not a valid mercurial repository' % (dest, uri)
                raise InvalidMercurialRepositoryError(message)
        else:
            raise interfaces.InvalidUrlError('this uri \'%s\' is invalid' % uri)

    def fetch(self, uri, dest, opts=None):
        """fetch a package
        Arguments:
            - uri : check out/update uri
            - dest: destination to fetch to
            - opts : arguments for the fetcher

                - revision: particular revision to deal with.

        Exceptions:
            - InvalidMercurialRepositoryError in case of repo problems
            - interfaces.FetchErrorin case of fetch problems
            - interfaces.InvalidUrlError in case of uri is invalid
        """
        if opts is None:
            opts = {}
        revision = opts.get('revision','tip')
        if self.is_valid_src_uri(uri):
            self._scm_cmd('clone %s %s' % (uri, dest))
            self._scm_cmd('up  -r %s -R %s' % (revision, dest))
            if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
                message = 'Unexpected fetch error on \'%s\'\n' % uri
                message += 'The directory \'%s\' is not a valid mercurial repository' % (dest, uri)
                raise InvalidMercurialRepositoryError(message)
        else:
            raise interfaces.InvalidUrlError('this uri \'%s\' is invalid' % uri)

    def fetch_or_update(self, uri, dest, opts = None):
        """see interface"""
        if os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
           self.update(uri, dest, opts)
        else:
           self.fetch(uri, dest, opts)

    def is_valid_src_uri(self, uri):
        """see interface"""
        m = interfaces.URI_REGEX.match(uri)
        if m and m.groups()[1] in ['file', 'hg', 'ssh', 'http', 'https']:
            return True
        return False

    def match(self, switch):
        """see interface"""
        if switch == 'hg':
            return True
        return False

    def _has_uri_changed(self, uri, dest):
        """see interface"""
        # file is removed on the local uris
        uri= uri.replace('file://','')
        # in case we were not hg before
        if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
            return True
        else:
            try:
                cwd = os.getcwd()
                os.chdir(dest)
                pr = subprocess.Popen('%s %s' % (self.executable, 'showconfig |grep paths.default'), shell = True, stdout=subprocess.PIPE)
                ret = pr.wait()
                if ret != 0:
                    raise interfaces.FetcherRuntimmeError('%s failed to achieve correctly.' % self.name)
                dest_uri = re.sub('([^=]*=)\s*(.*)', '\\2', pr.stdout.read().strip())
                os.chdir(cwd)
                if uri != dest_uri:
                    return True
            except Exception, e:
                os.chdir(cwd)
                raise e
        return False


class SvnFetcher(interfaces.IFetcher):
    """ Subversion Fetcher
    Example::
        >>> import minitage.core.fetchers.scm
        >>> svn = scm.SvnFetcher()
        >>> svn.fetch_or_update('http://uri','/dir',{revision='HEAD'})
    """

    def __init__(self, config = None):
        if not config:
            config = {}
        interfaces.IFetcher.__init__(self, 'subversion', 'svn', config, '.svn')

    def update(self, uri, dest, opts=None):
        """update a package
        Arguments:
            - uri : check out/update uri
            - dest: destination to fetch to
            - opts : arguments for the fetcher

                - revision: particular revision to deal with.

        Exceptions:
            - InvalidMercurialRepositoryError in case of repo problems
            - interfaces.FetchErrorin case of fetch problems
            - interfaces.InvalidUrlError in case of uri is invalid
        """
        if opts is None:
            opts = {}
        revision = opts.get('revision','HEAD')
        if self.is_valid_src_uri(uri):
            if self._has_uri_changed(uri, dest):
                self._remove_versionned_directories(dest)
            self._scm_cmd('up -r %s %s' % (revision, dest))
            if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
                message = 'Unexpected fetch error on \'%s\'\n' % uri
                message += 'The directory \'%s\' is not a valid subversion repository' % (dest, uri)
                raise InvalidMercurialRepositoryError(message)
        else:
            raise interfaces.InvalidUrlError('this uri \'%s\' is invalid' % uri)

    def fetch(self, uri, dest, opts=None):
        """fetch a package
        Arguments:
            - uri : check out/update uri
            - dest: destination to fetch to
            - opts : arguments for the fetcher

                - revision: particular revision to deal with.

        Exceptions:
            - InvalidMercurialRepositoryError in case of repo problems
            - interfaces.FetchErrorin case of fetch problems
            - interfaces.InvalidUrlError in case of uri is invalid
        """
        if opts is None:
            opts = {}
        revision = opts.get('revision','HEAD')
        if self.is_valid_src_uri(uri):
            self._scm_cmd('co -r %s %s %s' % (revision, uri,dest))
            if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
                message = 'Unexpected fetch error on \'%s\'\n' % uri
                message += 'The directory \'%s\' is not a valid subversion repository' % (dest, uri)
                raise InvalidMercurialRepositoryError(message)
        else:
            raise interfaces.InvalidUrlError('this uri \'%s\' is invalid' % uri)

    def fetch_or_update(self, uri, dest, opts = None):
        """see interface"""
        if os.path.isdir(dest):
           self.update(uri, dest, opts)
        else:
           self.fetch(uri, dest, opts)

    def is_valid_src_uri(self, uri):
        """see interface"""
        m = interfaces.URI_REGEX.match(uri)
        if m and m.groups()[1] in ['file', 'svn', 'svn+ssh', 'http', 'https']:
            return True
        return False

    def match(self, switch):
        """see interface"""
        if switch == 'svn':
            return True
        return False

    def _has_uri_changed(self, uri, dest):
        """see interface"""
        pr = subprocess.Popen('%s %s' % (self.executable, 'info %s|grep -i url' % dest), shell = True, stdout=subprocess.PIPE)
        ret = pr.wait()
        # we werent svn
        if ret != 0:
            return True
        dest_uri = re.sub('([^:]*:)\s*(.*)', '\\2', pr.stdout.read().strip())
        if uri != dest_uri:
            return True
        return False

# vim:set et sts=4 ts=4 tw=80:
