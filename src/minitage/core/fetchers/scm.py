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

import os
import subprocess
import re
import datetime
import logging

from minitage.core.fetchers import interfaces

__logger__ = 'minitage.fetchers.scm'

class InvalidMercurialRepositoryError(interfaces.InvalidRepositoryError):
    """Mercurial repository is invalid."""

class InvalidBazaarRepositoryError(interfaces.InvalidRepositoryError):
    """Bazaar repository is invalid."""

class InvalidGitRepositoryError(interfaces.InvalidRepositoryError):
    """Git repository is invalid.""" 

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

    def update(self, dest, uri = None, opts=None, verbose=False):
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
        args = opts.get('args','')
        if not uri or self.is_valid_src_uri(uri):
            if uri and self._has_uri_changed(dest, uri):
                self._remove_versionned_directories(dest)
                self._scm_cmd('init %s' % (dest), verbose)
                if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
                    message = 'Unexpected fetch error on \'%s\'\n' % uri
                    message += 'The directory \'%s\' is not '
                    message += 'a valid mercurial repository' % (dest)
                    raise InvalidMercurialRepositoryError(message)
            if uri:
                self._scm_cmd('pull -f %s -R %s' % (uri, dest), verbose)
            else:
                self._scm_cmd('pull -f -R %s' % (dest), verbose)
            self._scm_cmd('  up -r %s -R %s ' % (revision, dest), verbose)
            if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
                message = 'Unexpected fetch error on \'%s\'\n' % uri
                message += 'The directory \'%s\' is not '
                message += 'a valid mercurial repository' % (dest, uri)
                raise InvalidMercurialRepositoryError(message)
        else:
            raise interfaces.InvalidUrlError('this uri \'%s\' is invalid' % uri)

    def fetch(self, dest, uri, opts=None, verbose=False):
        """Fetch a package.
        Arguments:
            - uri : check out/update uri
            - dest: destination to fetch to
            - opts : arguments for the fetcher

                - revision: particular revision to deal with.
                - args: misc arguments to give

        Exceptions:
            - InvalidMercurialRepositoryError in case of repo problems
            - interfaces.FetchErrorin case of fetch problems
            - interfaces.InvalidUrlError in case of uri is invalid
        """
        if opts is None:
            opts = {}
        revision = opts.get('revision','tip')
        args = opts.get('args','')
        # move directory that musnt be there !
        if os.path.isdir(dest):
            os.rename(dest, '%s.old.%s' \
                      % (dest, datetime.datetime.now().strftime('%d%m%y%H%M%S'))
                     )
        if self.is_valid_src_uri(uri):
            self._scm_cmd('clone %s %s %s' % (args, uri, dest), verbose)
            self._scm_cmd('up  -r %s %s -R %s' % (revision, args, dest), verbose)
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
           and (match.groups()[2] in ['file', 'hg', 'ssh', 'http', 'https', '/']
                or match.groups()[0] == '/'):
            return True
        return False

    def match(self, switch):
        """See interface."""
        if switch == 'hg':
            return True
        return False


    def get_uri(self, dest):
        """get mercurial url"""
        self._check_scm_presence()
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
        self.log = logging.getLogger(__logger__)

    def update(self, dest, uri = None, opts=None, verbose=False):
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
        revision = opts.get('revision','HEAD')
        args = opts.get('args','')
        if not uri or self.is_valid_src_uri(uri):
            if uri and self._has_uri_changed(dest, uri):
                self._remove_versionned_directories(dest)
            self._scm_cmd('up %s -r %s %s' % (args, revision, dest), verbose)
            if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
                message = 'Unexpected fetch error on \'%s\'\n' % uri
                message += 'The directory \'%s\' is not '
                message += 'a valid subversion repository' % (dest, uri)
                raise InvalidMercurialRepositoryError(message)
        else:
            raise interfaces.InvalidUrlError('this uri \'%s\' is invalid' % uri)

    def fetch(self, dest, uri, opts=None, verbose=False):
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
        args = opts.get('args','')
        if self.is_valid_src_uri(uri):
            self._scm_cmd('co %s -r %s %s %s' % (args, revision, uri, dest), verbose)
            self.log.info('SVN checkout completed')
            if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
                message = 'Unexpected fetch error on \'%s\'\n' % uri
                message += 'The directory \'%s\' is not '
                message += 'a valid subversion repository' % (dest, uri)
                raise InvalidMercurialRepositoryError(message)
        else:
            raise interfaces.InvalidUrlError('this uri \'%s\' is invalid' % uri)

    def is_valid_src_uri(self, uri):
        """See interface."""
        match = interfaces.URI_REGEX.match(uri)
        if match \
           and match.groups()[2] \
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
        self._check_scm_presence()
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


class BzrFetcher(interfaces.IFetcher):
    """ Bazaar Fetcher.
    Example::
        >>> import minitage.core.fetchers.scm
        >>> bzr = scm.BzrFetcher()
        >>> bzr.fetch_or_update('http://uri','/dir',{revision='last:1'})
    """

    def __init__(self, config = None):
        self.config =  config
        interfaces.IFetcher.__init__(self, 'bazaar', 'bzr', config, '.bzr')
        self.log = logging.getLogger(__logger__)

    def update(self, dest, uri = None, opts=None, verbose=False):
        """Update a package.
        Arguments:
            - uri : check out/update uri
            - dest: destination to fetch to
            - opts : arguments for the fetcher

                - revision: particular revision to deal with.

        Exceptions:
            - InvalidBazaarRepositoryError in case of repo problems
            - interfaces.FetchErrorin case of fetch problems
            - interfaces.InvalidUrlError in case of uri is invalid
        """
        self.log.debug('Updating %s / %s' % (dest, uri))
        if opts is None:
            opts = {}
        revision = opts.get('revision','last:1')
        args = opts.get('args','')
        if not uri or self.is_valid_src_uri(uri):
            if uri and self._has_uri_changed(dest, uri):
                self._remove_versionned_directories(dest)
                self._scm_cmd('init %s' % (dest), verbose)
                if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
                    message = 'Unexpected fetch error on \'%s\'\n' % uri
                    message += 'The directory \'%s\' is not '
                    message += 'a valid bazaar repository' % (dest)
                    raise InvalidBazaarRepositoryError(message)
            if uri:
                self._scm_cmd('pull --overwrite -r%s %s -d %s' % (revision, uri, dest), verbose)
            else:
                self._scm_cmd('pull --overwrite -r%s    -d %s' % (revision, dest), verbose)
            if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
                message = 'Unexpected fetch error on \'%s\'\n' % uri
                message += 'The directory \'%s\' is not '
                message += 'a valid bazaar repository' % (dest, uri)
                raise InvalidBazaarRepositoryError(message)
        else:
            raise interfaces.InvalidUrlError('this uri \'%s\' is invalid' % uri)


    def fetch(self, dest, uri, opts=None, verbose=False):
        """Fetch a package.
        Arguments:
            - uri : check out/update uri
            - dest: destination to fetch to
            - opts : arguments for the fetcher

                - revision: particular revision to deal with.
                - args: misc arguments to give

        Exceptions:
            - InvalidBazaarRepositoryError in case of repo problems
            - interfaces.FetchErrorin case of fetch problems
            - interfaces.InvalidUrlError in case of uri is invalid
        """
        if opts is None:
            opts = {}
        revision = opts.get('revision','last:1')
        args = opts.get('args','')
        # move directory that musnt be there !
        if os.path.isdir(dest):
            os.rename(dest, '%s.old.%s' \
                      % (dest, datetime.datetime.now().strftime('%d%m%y%H%M%S'))
                     )
        if self.is_valid_src_uri(uri):
            self._scm_cmd('checkout  -r %s %s %s %s' % (revision, args, uri, dest), verbose)
            if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
                message = 'Unexpected fetch error on \'%s\'\n' % uri
                message += 'The directory \'%s\' is not '
                message += 'a valid bazaar repository' % (dest, uri)
                raise InvalidBazaarRepositoryError(message)
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
        bzrmatch = re.compile('[a-zA-Z1-9]*:(.*)').match(uri)
        if match \
           and match.groups()[2] \
           in ['file', 'bzr', 'sftp', 'http',
               'https', 'bzr+http', 'bzr+https',
               'bzr+ssh', 'svn+file',
               'svn', 'svn+http', 'svn+https'] or bzrmatch:
            return True
        return False

    def match(self, switch):
        """See interface."""
        if switch == 'bzr':
            return True
        return False


    def get_uri(self, dest):
        """get bazaar url"""
        self._check_scm_presence()
        try:
            cwd = os.getcwd()
            os.chdir(dest)
            self.log.debug('Running %s %s in %s' % (
                self.executable,
                ' info 2>&1|egrep "(checkout of branch|parent branch)"|cut -d:  -f 2,3',
                dest
            ))
            process = subprocess.Popen(
                '%s %s' % (
                    self.executable,
                    ' info 2>&1|egrep "(checkout of branch|parent branch)"|cut -d:  -f 2,3',
                ),
                shell = True, stdout=subprocess.PIPE
            )
            ret = process.wait()
            if ret != 0:
                message = '%s failed to achieve correctly.' % self.name
                raise interfaces.FetcherRuntimeError(message)
            dest_uri = re.sub(
                '([^=]*=)\s*(.*)',
                '\\2',
                process.stdout.read().strip()
            )
            os.chdir(cwd)
            return dest_uri
        except Exception, instance:
            os.chdir(cwd)
            raise instance

    def _has_uri_changed(self, dest, uri):
        """See interface."""
        # file is removed on the local uris
        uri = uri.replace('file://', '')
        # in case we were not bzr before
        if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
            return True
        elif uri != self.get_uri(dest):
            return True
        return False


class GitFetcher(interfaces.IFetcher):
    """ Bazaar Fetcher.
    Example::
        >>> import minitage.core.fetchers.scm
        >>> git = scm.GitFetcher()
        >>> git.fetch_or_update('http://uri','/dir',{revision='head'})
    """

    def __init__(self, config = None):
        self.config =  config
        interfaces.IFetcher.__init__(self, 'git', 'git', config, '.git')
        self.log = logging.getLogger(__logger__)

    def update(self, dest, uri = None, opts=None, verbose=False):
        """Update a package.
        Arguments:
            - uri : check out/update uri
            - dest: destination to fetch to
            - opts : arguments for the fetcher

                - revision: particular revision to deal with.

        Exceptions:
            - InvalidBazaarRepositoryError in case of repo problems
            - interfaces.FetchErrorin case of fetch problems
            - interfaces.InvalidUrlError in case of uri is invalid
        """
        self.log.debug('Updating %s / %s' % (dest, uri))
        if opts is None:
            opts = {}
        revision = opts.get('revision', 'HEAD')
        args = opts.get('args','')
        if not uri or self.is_valid_src_uri(uri):
            if uri and self._has_uri_changed(dest, uri):
                self._remove_versionned_directories(dest)
                cwd = os.getcwd()
                os.chdir(dest)
                self._scm_cmd('init', verbose)
                if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
                    message = 'Unexpected fetch error on \'%s\'\n' % uri
                    message += 'The directory \'%s\' is not ' % (dest)
                    message += 'a valid git repository'
                    raise InvalidGitRepositoryError(message)
                self._scm_cmd('pull -f %s' % (uri), verbose)
                self._scm_cmd('reset --hard %s ' % (revision), verbose)
                os.chdir(cwd)
            else:
                cwd = os.getcwd()
                os.chdir(dest)
                suri = ''
                if uri:
                    suri = '%s' % suri
                self._scm_cmd('reset --hard', verbose)
                self._scm_cmd('pull --f %s' % suri, verbose)
                self._scm_cmd('reset --hard %s' % (revision), verbose)
                os.chdir(cwd)
            if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
                message = 'Unexpected fetch error on \'%s\'\n' % uri
                message += 'The directory \'%s\' is not '
                message += 'a valid bazaar repository' % (dest, uri)
                raise InvalidGitRepositoryError(message)
        else:
            raise interfaces.InvalidUrlError('this uri \'%s\' is invalid' % uri)


    def fetch(self, dest, uri, opts=None, verbose=False):
        """Fetch a package.
        Arguments:
            - uri : check out/update uri
            - dest: destination to fetch to
            - opts : arguments for the fetcher

                - revision: particular revision to deal with.
                - args: misc arguments to give

        Exceptions:
            - InvalidBazaarRepositoryError in case of repo problems
            - interfaces.FetchErrorin case of fetch problems
            - interfaces.InvalidUrlError in case of uri is invalid
        """
        cwd = os.getcwd()
        os.chdir('/')
        if opts is None:
            opts = {}
        revision = opts.get('revision','HEAD')
        args = opts.get('args','')
        # move directory that musnt be there !
        if os.path.isdir(dest):
            os.rename(dest, '%s.old.%s' \
                      % (dest, datetime.datetime.now().strftime('%d%m%y%H%M%S'))
                     )
        if self.is_valid_src_uri(uri):
            self._scm_cmd('clone  %s %s %s' % (args, uri, dest), verbose)
            os.chdir(dest)
            self._scm_cmd('reset --hard %s ' % (revision), verbose)
            os.chdir(cwd)
            if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
                message = 'Unexpected fetch error on \'%s\'\n' % uri
                message += 'The directory \'%s\' is not '
                message += 'a valid bazaar repository' % (dest, uri)
                raise InvalidGitRepositoryError(message)
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
        gitmatch = re.compile('[a-zA-Z1-9]*:(.*)').match(uri)
        if match \
           and match.groups()[2] \
           in ['file', 'git', 'rsync', 'http',
               'https', 'svn'] or gitmatch:
            return True
        return False

    def match(self, switch):
        """See interface."""
        if switch == 'git':
            return True
        return False


    def get_uri(self, dest):
        """get git url"""
        self._check_scm_presence()
        try:
            cwd = os.getcwd()
            os.chdir(dest)
            self.log.debug('Running %s %s in %s' % (
                self.executable,
                'config --get remote.origin.url',
                dest
            ))
            process = subprocess.Popen('%s config --get remote.origin.url' % self.executable,
                                       shell = True, stdout=subprocess.PIPE)
            ret = process.wait()
            if ret >1 :
                message = '%s failed to achieve correctly.' % self.name
                raise interfaces.FetcherRuntimeError(message)
            dest_uri = process.stdout.read().strip()
            os.chdir(cwd)
            return dest_uri
        except Exception, instance:
            os.chdir(cwd)
            raise instance

    def _has_uri_changed(self, dest, uri):
        """See interface."""
        # in case we were not git before
        if not os.path.isdir('%s/%s' % (dest, self.metadata_directory)):
            return True
        elif uri != self.get_uri(dest):
            return True
        return False


# vim:set et sts=4 ts=4 tw=80:
