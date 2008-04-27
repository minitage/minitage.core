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

class NoPackagesError(Exception): pass
class ConflictModesError(Exception): pass
class InvalidConfigFileError(Exception): pass
class TooMuchActionsError(Exception): pass
class CliError(Exception): pass

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
        self.packages = options.get('packages', False)
        self.debug = options.get('debug', self.config._sections.get('minimerge', {}).get('debug', False))
        self.fetchonly = options.get('fetchonly', False)
        self.offline = options.get('offline', self.config._sections.get('minimerge', {}).get('offline', False))

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
        self.minilays = [dir for dir in minilays_search_paths if os.path.isdir(dir)]

    def _find_minibuild(self,package):
        ''''''
        pass

    def _compute_dependencies(self):
        ''''''
        for package in self.packages:
            self._find_minibuild(package)

    def main(self,options):
        '''Main loop :
          ------------
          Here executing the minimerge tasks:
              - calculate dependencies
              - for each dependencies:
                  - maybe fetch
                  - maybe update
                  - maybe install
                  - maybe remove
        '''

        if not self.nodeps:
            self._compute_dependencies()


