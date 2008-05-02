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

class MinimergeError(Exception): pass
class NoPackagesError(MinimergeError): pass
class ConflictModesError(MinimergeError): pass
class InvalidConfigFileError(MinimergeError): pass
class TooMuchActionsError(MinimergeError): pass
class CliError(MinimergeError): pass
class MinibuildNotFoundError(MinimergeError): pass
class CircurlarDependencyError(MinimergeError): pass

class Minimerge(object):

    def __init__(self,options={}):
        '''Options are taken from the section 'minimerge' in the configuration file
        then can be overriden in the input dictionnary.
        :Parameters:
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
        '''
        # first try to read the config in
        # - command line
        # - exec_prefix
        # - ~/.minimerge.cfg
        # We have the corresponding file allready filled in option.config, see
        # `minimerge.core.cli`
        self.config_path = os.path.expanduser(options.get('config'))
        self.config = ConfigParser.ConfigParser()
        try:
            self.config.read(self.config_path)
        except:
            raise InvalidConfigFileError('The configuration file is invalid: %s' % self.config_path)

        # prefix is setted in the configuration file
        # it defaults to sys.exec_prefix
        self.prefix = self.config._sections.get('minimerge', {}).get('prefix', sys.exec_prefix)

        # modes
        # for offline and debug mode, we see too if the flag is not set in the
        # configuration file
        self.jump = options.get('jump', False)
        self.nodeps = options.get('nodeps', False)
        self.debug = options.get('debug', self.config._sections.get('minimerge', {}).get('debug', False))
        self.fetchonly = options.get('fetchonly', False)
        self.offline = options.get('offline', self.config._sections.get('minimerge', {}).get('offline', False))

        self.packages = options.get('packages', False)
        self.computed_packages = []

        # what are we doing
        self.action = options.get('action', False)

        self.minilays = []
        minilays_search_paths = []
        # minilays can be ovvrided by env["MINILAYS"]
        minilays_search_paths.extend(os.environ.get('MINILAYS', '').strip().split())
        # minilays are in minilays/
        minilays_parent = '%s/%s' % (self.prefix, 'minilays')
        if os.path.isdir(minilays_parent):
            minilays_search_paths.extend(['%s/%s' % (minilays_parent, dir) for dir in os.listdir(minilays_parent)])
        # they are too in etc/minmerge.cfg[minilays]
        minilays_search_paths.extend(self.config._sections.get('minimerge', {}).get('minilays', '').strip().split())

        # filtering valid ones
        # and mutating into real Minilays objects
        self.minilays = [objects.Minilay(path = os.path.expanduser(dir)) \
                         for dir in minilays_search_paths if os.path.isdir(dir)]

    def _find_minibuild(self, package):
        '''
        @param package str minibuild to find
        Exceptions
            - raises MinibuildNotFoundError if the packages is not found is any minilay.
        Returns
            - The minibuild found
        '''
        for minilay in self.minilays:
            if package in minilay:
                return minilay[package]
        raise MinibuildNotFoundError('Tahe minibuild \'%s\' was not found' % package)

    def _compute_dependencies(self,packages = [],*kw,**kwargs):
        '''
        @param package list list of packages to get the deps
        @param ancestors list list of tuple(ancestor,level of dependency)
        Exceptions
            - raises CircurlarDependencyError in case of curcular dependencies trees
        Returns
            - Nothing but self.computed_packages is filled with needed
            dependencies. Not that this list must be reversed.'''
        ancestors = kwargs.get('ancestors',[])
        for package in packages:
            mb = self._find_minibuild(package)
            # test if we have not already the package in our dependency list, then
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
                ancestors = self._compute_dependencies(mb.dependencies,ancestors=ancestors)
            except RuntimeError,e:
                if str(e) == 'maximum recursion depth exceeded in cmp':
                    message = 'Circular dependency detected around %s and ancestors: \'%s\''
                    raise CircurlarDependencyError(message % (mb.name, [m.name for m in ancestors]))
        return ancestors

    def main(self,options):
        '''Main loop :
          ------------
          Here executing the minimerge tasks:
              - calculate dependencies
              - for each dependencies:
                  - maybe fetch / update
                  - maybe install
                  - maybe remove
        '''
        if not self.nodeps:
            self.computed_packages = self._compute_dependencies(self.packages)
            # we need to merge in the reverse order that we computed deps
            self.computed_packages.reverse()

