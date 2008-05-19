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
import subprocess
import re
import shutil
import datetime
import logging

from minitage.core.fetchers import interfaces

__logger__ = 'minitage.fetchers.scm'

class InvalidMercurialRepositoryError(interfaces.InvalidRepositoryError):
    """Mercurial repository is invalid."""


class OfflineModeRestrictionError(interfaces.IFetcherError):
    """Restriction error in offline mode."""


class HgFetcher(interfaces.IFetcher):
    """ Mercurial Fetcher.
    Example::
        >>> import minitage.core.fetchers.scm
        >>> hg = scm.HgFetcher()
        >>> hg.fetch_or_update('http://uri','/dir',{revision='tip'})
    """

    def __init__(self, config = None):
        self.config =  config
        interfaces.IFetcher.__init__(self, 'mercurial', 'hg', config, '.hg')
        self.log = logging.getLogger(__logger__)

    def update(self, dest, uri = None, opts=None):
        """Update a package.
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
        self.log.debug('Updating %s / %s' % (dest, uri))
        if opts is None:
            opts = {}
        revision = opts.get('revision','tip')
        if not uri or self.is_valid_src_uri(uri):
            if uri and self._has_uri_changed(dest, uri):
                self._remove_versionned_directories(dest)
                self._scm_cmd('init %s' % (dest))
                if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
                    message = 'Unexpected fetch error on \'%s\'\n' % uri
                    message += 'The directory \'%s\' is not '
                    message += 'a valid mercurial repository' % (dest)
                    raise InvalidMercurialRepositoryError(message)
            if uri:
                self._scm_cmd('pull -f %s -R %s' % (uri, dest))
            else:
                self._scm_cmd('pull -f -R %s' % (dest))
            self._scm_cmd('  up -r %s -R %s ' % (revision, dest))
            if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
                message = 'Unexpected fetch error on \'%s\'\n' % uri
                message += 'The directory \'%s\' is not '
                message += 'a valid mercurial repository' % (dest, uri)
                raise InvalidMercurialRepositoryError(message)
        else:
            raise interfaces.InvalidUrlError('this uri \'%s\' is invalid' % uri)

    def fetch(self, dest, uri, opts=None):
        """Fetch a package.
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
        # move directory that musnt be there !
        if os.path.isdir(dest):
            os.rename(dest, '%s.old.%s' \
                      % (dest, datetime.datetime.now().strftime('%d%m%y%H%M%S'))
                     )
        if self.is_valid_src_uri(uri):
            self._scm_cmd('clone %s %s' % (uri, dest))
            self._scm_cmd('up  -r %s -R %s' % (revision, dest))
            if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
                message = 'Unexpected fetch error on \'%s\'\n' % uri
                message += 'The directory \'%s\' is not '
                message += 'a valid mercurial repository' % (dest, uri)
                raise InvalidMercurialRepositoryError(message)
        else:
            raise interfaces.InvalidUrlError('this uri \'%s\' is invalid' % uri)

    def fetch_or_update(self, dest, uri, opts = None):
        """See interface."""
        if os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
            self.update(dest, uri, opts)
        else:
            self.fetch(dest, uri, opts)

    def is_valid_src_uri(self, uri):
        """See interface."""
        match = interfaces.URI_REGEX.match(uri)
        if match \
           and match.groups()[1] \
           in ['file', 'hg', 'ssh', 'http', 'https']:
            return True
        return False

    def match(self, switch):
        """See interface."""
        if switch == 'hg':
            return True
        return False


    def get_uri(self, dest):
        """get mercurial url"""
        try:
            cwd = os.getcwd()
            os.chdir(dest)
            self.log.debug('Running %s %s in %s' % (
                self.executable,
                'showconfig |grep paths.default',
                dest
            ))
            process = subprocess.Popen(
                '%s %s' % (
                    self.executable,
                    'showconfig |grep paths.default'
                ),
                shell = True, stdout=subprocess.PIPE
            )
            ret = process.wait()
            if ret != 0:
                message = '%s failed to achieve correctly.' % self.name
                raise interfaces.FetcherRuntimeError(message)
            dest_uri = re.sub('([^=]*=)\s*(.*)',
                          '\\2',
                          process.stdout.read().strip()
                         )
            os.chdir(cwd)
            return dest_uri
        except Exception, instance:
            import pdb;pdb.set_trace()  ## Breakpoint ##
            os.chdir(cwd)
            raise instance

    def _has_uri_changed(self, dest, uri):
        """See interface."""
        # file is removed on the local uris
        uri = uri.replace('file://', '')
        # in case we were not hg before
        if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
            return True
        elif uri != self.get_uri(dest):
                return True
        return False


class SvnFetcher(interfaces.IFetcher):
    """Subversion Fetcher.
    Example::
        >>> import minitage.core.fetchers.scm
        >>> svn = scm.SvnFetcher()
        >>> svn.fetch_or_update('http://uri','/dir',{revision='HEAD'})
    """

    def __init__(self, config = None):
        self.config =  config
        interfaces.IFetcher.__init__(self, 'subversion', 'svn', config, '.svn')

    def update(self, dest, uri = None, opts=None):
        """Update a package.
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
        log = logging.getLogger(__logger__)
        log.debug('Updating %s / %s' % (dest, uri))
        if opts is None:
            opts = {}
        revision = opts.get('revision','HEAD')
        if not uri or self.is_valid_src_uri(uri):
            if uri and self._has_uri_changed(dest, uri):
                self._remove_versionned_directories(dest)
            self._scm_cmd('up -r %s %s' % (revision, dest))
            if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
                message = 'Unexpected fetch error on \'%s\'\n' % uri
                message += 'The directory \'%s\' is not '
                message += 'a valid subversion repository' % (dest, uri)
                raise InvalidMercurialRepositoryError(message)
        else:
            raise interfaces.InvalidUrlError('this uri \'%s\' is invalid' % uri)

    def fetch(self, dest, uri, opts=None):
        """Fetch a package.
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
            self._scm_cmd('co -r %s %s %s' % (revision, uri, dest))
            if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
                message = 'Unexpected fetch error on \'%s\'\n' % uri
                message += 'The directory \'%s\' is not '
                message += 'a valid subversion repository' % (dest, uri)
                raise InvalidMercurialRepositoryError(message)
        else:
            raise interfaces.InvalidUrlError('this uri \'%s\' is invalid' % uri)

    def fetch_or_update(self, dest, uri, opts = None):
        """See interface."""
        if os.path.isdir(dest):
            self.update(dest, uri, opts)
        else:
            self.fetch(dest, uri, opts)

    def is_valid_src_uri(self, uri):
        """See interface."""
        match = interfaces.URI_REGEX.match(uri)
        if match \
           and match.groups()[1] \
           in ['file', 'svn', 'svn+ssh', 'http', 'https']:
            return True
        return False

    def match(self, switch):
        """See interface."""
        if switch == 'svn':
            return True
        return False


    def get_uri(self, dest):
        """Get url."""
        process = subprocess.Popen(
            '%s %s' % (
                self.executable,
                'info %s|grep -i url' % dest
            ),
            shell = True, stdout=subprocess.PIPE
        )
        ret = process.wait()
        # we werent svn
        if ret != 0:
            return None
        return re.sub('([^:]*:)\s*(.*)', '\\2',
                          process.stdout.read().strip()
                         )

    def _has_uri_changed(self, dest, uri):
        """See interface."""
        if uri != self.get_uri(dest):
            return True
        return False

# vim:set et sts=4 ts=4 tw=80:
