# Copyright (C)2008 'Mathieu PASQUET <kiorky@cryptelium.net> '
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

__docformat__ = 'restructuredtext en'
version = '0.0.4'

import os
import sys
import ConfigParser

from minitage.core import objects
from minitage.core.fetchers.interfaces import IFetcherFactory

class MinimergeError(Exception):
    """General Minimerge Error"""


class NoPackagesError(MinimergeError):
    """No packages are given to merge"""


class ConflictModesError(MinimergeError):
    """Minimerge used without arguments."""


class InvalidConfigFileError(MinimergeError): 
    """Minimerge config file is not valid."""


class TooMuchActionsError(MinimergeError): 
    """Too much actions are given to do"""


class CliError(MinimergeError): 
    """General command line error"""


class MinibuildNotFoundError(MinimergeError): 
    """Minibuild is not found."""


class CircurlarDependencyError(MinimergeError): 
    """There are circular dependencies in the dependency tree"""


class Minimerge(object):
    """Minimerge object."""

    def __init__(self, options=None):
        """Options are taken from the section 'minimerge'
        in the configuration file  then can be overriden
        in the input dictionnary.
        Arguments:
            - options:

                - jump: package in the dependency tree to jump to
                - packages: packages list to handle *mandatory*
                - debug: debug mode
                - fetchonly: just get the packages
                - offline: do not try to connect outside
                - nodeps: Squizzes all dependencies
                - action: what to do *mandatory*
                - sync: sync mode
                - config: configuration file path *mandatory*
        """
        if options is None:
            options = {}
        # first try to read the config in
        # - command line
        # - exec_prefix
        # - ~/.minimerge.cfg
        # We have the corresponding file allready filled in option._config, see
        # `minimerge.core.cli`
        #
        self._config_path = os.path.expanduser(options.get('config'))
        self._config = ConfigParser.ConfigParser()
        try:
            self._config.read(self._config_path)
        except:
            message = 'The configuration file is invalid: %s' % self._config_path
            raise InvalidConfigFileError(message)

        # prefix is setted in the configuration file
        # it defaults to sys.exec_prefix
        self._prefix = self._config._sections.get('minimerge', {}) \
                                .get('prefix', sys.exec_prefix)

        # modes
        # for offline and debug mode, we see too if the flag is not set in the
        # configuration file
        self._jump = options.get('jump', False)
        self._nodeps = options.get('nodeps', False)
        self._debug = options.get('debug', self._config._sections\
                                  .get('minimerge', {}).get('debug', False))
        self._fetchonly = options.get('fetchonly', False)
        self._offline = options.get('offline', self._config._sections\
                                    .get('minimerge', {}).get('offline', False))

        self._packages = options.get('packages', False)

        # what are we doing
        self._action = options.get('action', False)

        self._minilays = []
        minilays_search_paths = []
        # minilays can be ovvrided by env["MINILAYS"]
        minilays_search_paths.extend(
            os.environ.get('MINILAYS', '').strip().split()
        )
        # minilays are in minilays/
        minilays_parent = '%s/%s' % (self._prefix, 'minilays')
        if os.path.isdir(minilays_parent):
            minilays_search_paths.extend(['%s/%s' % (minilays_parent, dir)
                                        for dir in os.listdir(minilays_parent)])
        # they are too in etc/minmerge.cfg[minilays]
        minimerge_section = self._config._sections.get('minimerge', {})
        minilays_section = minimerge_section.get('minilays', '')
        minilays_search_paths.extend(minilays_section.strip().split())

        # filtering valid ones
        # and mutating into real Minilays objects
        self._minilays = [objects.Minilay(path = os.path.expanduser(dir)) \
                         for dir in minilays_search_paths if os.path.isdir(dir)]

    def _find_minibuild(self, package):
        """
        @param package str minibuild to find
        Exceptions
            - MinibuildNotFoundError if the packages is not found is any minilay.

        Returns
            - The minibuild found
        """
        for minilay in self._minilays:
            if package in minilay:
                return minilay[package]
        message = 'Tahe minibuild \'%s\' was not found' % package
        raise MinibuildNotFoundError(message)

    def _compute_dependencies(self, packages = None, ancestors = None):
        """
        @param package list list of packages to get the deps
        @param ancestors list list of tuple(ancestor,level of dependency)
        Exceptions
            - CircurlarDependencyError in case of curcular dependencies trees

        Returns
            - Nothing but self.computed_packages is filled with needed
            dependencies. Not that this list must be reversed.
        """
        if packages is None:
            packages = []
        if ancestors is None:
            ancestors = []

        for package in packages:
            mb = self._find_minibuild(package)
            # test if we have not already the package in our deps list, then
            # ...
            # if we have no ancestor, the end of the list is fine.
            index = len(ancestors)
            # if we have ancestors
            if ancestors:
                # we must check ancestor installation priority:
                #  we must install dependencies prior to the first
                #  package which have the dependency in its list
                for ancestor in ancestors:
                    if mb.name in ancestor.dependencies:
                        index = ancestors.index(ancestor)
                        break
            # last check if package is not already there.
            if not mb in ancestors:
                ancestors.insert(index, mb)
            # unconditionnaly parsing dependencies, even if the package is
            # already there to detect circular dependencies
            try:
                ancestors = self._compute_dependencies(mb.dependencies,
                                                       ancestors=ancestors)
            except RuntimeError,e:
                message = 'Circular dependency around %s and ancestors: \'%s\''
                raise CircurlarDependencyError(message %
                                         (mb.name, [m.name for m in ancestors]))
        return ancestors

    def _fetch(self, package):
        """
        @param param minitage.core.objects.Minibuid the minibuild to fetch
        Exceptions
           - MinimergeFetchComponentError if we do not found any component to
             fetch the package.
           - The fetcher exception.
        """
        dest_container = '%s/%s' % (self._prefix, package.category)
        fetcherFactory = IFetcherFactory(self._config_path)
        if not os.path.isdir(dest_container):
            os.makedirs(dest_container)
        fetcherFactory(package.src_type).fetch_or_update(
            package.src_uri,
            '%s/%s' % (dest_container, package.name)
        )

    def _do_action(self, package):
        """Do action."""
        pass


    def _cut_jumped_packages(self, packages):
        """Remove jumped packages."""
        try:
            i = packages.index(self._jump)
            packages = packages[i:]
        except:
            pass
        return packages

    def main(self):
        """Main loop.
          Here executing the minimerge tasks:
              - calculate dependencies
              - for each dependencies:

                  - maybe fetch / update
                  - maybe install
                  - maybe remove
        """
        packages = self._packages
        # compute dependencies
        if not self._nodeps:
            packages = self._compute_dependencies(self.packages)

        if self._jump:
            packages = self._cut_jumped_packages(packages)

        # fetch if not offline
        if not self._offline:
            for package in packages:
                self._fetch(package)

        # if we do not want just to fetch, let's go ,
        # (install|delete|reinstall) baby.
        if not self._fetchonly:
            for package in package:
                self._do_action(package)

