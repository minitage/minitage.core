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
from minitage.core.makers.interfaces   import IMakerFactory

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

class ActionError(MinimergeError):
    """General action error"""


class MinibuildNotFoundError(MinimergeError):
    """Minibuild is not found."""


class CircurlarDependencyError(MinimergeError):
    """There are circular dependencies in the dependency tree"""



PYTHON_VERSIONS = ('2.4', '2.5')

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
            message = 'The config file is invalid: %s' % self._config_path
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
        message = 'The minibuild \'%s\' was not found' % package
        raise MinibuildNotFoundError(message)

    def _find_minibuilds(self, packages):
        """
        @param package list minibuild to find
        Exceptions
            - MinibuildNotFoundError if the packages is not found is any minilay.

        Returns
            - The minibuild found
        """
        cpackages = []
        for package in packages:
            cpackages.append(self._find_minibuild(package))
        return cpackages

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
            '%s/%s' % (dest_container, package.name),
            package.src_uri,
        )

    def _do_action(self, action, packages):
        """Do action.
        Install, delete or reinstall a list of packages (minibuild instances).
        Arguments
            - action: reinstall|install|delete action to do.
            - packages: minibuilds to deal with in order!
        """
        # cut pythons we do not need !
        # also get the parts to do in 'eggs' buildout
        packages, pyvers = self._select_pythons(packages)
        maker_kwargs = {}

        mf = IMakerFactory(self._config_path)
        for package in packages:
            # if we are an egg, we maybe will have python versions setted.
            maker_kwargs['python_versions'] = pyvers.get(package.name, None)
            # we install unless we are dealing with a meta
            if not package.name.startswith('meta-'):
                options = {}

                ipath = '%s/%s/%s' % (self._prefix,
                                      package.category,
                                      package.name)
                maker = mf(package.install_method)
                options = maker.get_options(self, package, **maker_kwargs)

                # finally, time to act.
                if not os.path.isdir(ipath):
                    os.makedirs(ipath)
                callback = getattr(maker, action, None)
                if callback:
                    callback(ipath, options)
                else:
                    message = 'The action \'%s\' does not exists ' % action
                    message += 'in this \'%s\' component' \
                            % ( package.install_method)
                    raise ActionError(message)

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
                  - maybe delete
        """
        if self._action == 'sync':
            self._sync()
        else:
            packages = self._packages
            # compute dependencies
            if not self._nodeps:
                packages = self._compute_dependencies(self._packages)

            if self._jump:
                packages = self._cut_jumped_packages(packages)

            # fetch if not offline
            if not self._offline:
                for package in packages:
                    self._fetch(package)

            # if we do not want just to fetch, let's go ,
            # (install|delete|reinstall) baby.
            if not self._fetchonly:
                self._do_action(packages)

    def _select_pythons(self, packages):
        """Get pythons to build into dependencies.
        Handle multi site-packages is not that tricky:
            - We have to install python-major.minor only
              if we need it
            - We must build eggs site-packages only if
              we need them too.

        The idea i found is something like that:
            - We look in the packages to see if they want a
              particular python.

               * If a particular 'python-MAJOR.minor' is set in
                 the dependencies, we grab this version for selection.
               * If 'meta-python' is set in a direct dependency
                   (command line): we grab all available versions
               * If nothing is set, we let the dependency system continue
                 with what it has already.
            - Next, when we have selected pythons, we will delete others
              python from the dependency tree.
            - We put inside our selected python(s)
            - And we set too the parts to build for 'eggs' Minibuilds.

        Return
            - tuple with the according packages without uneeded stuff
              and a dict for the eggs with just the needed parts.
                ([new, packages, list], {'packagename': (buildout, parts)}
        """
        # select wich version of python are really needed.
        pyversions = []
        selected_pyver = {}
        stop = False

        # first look if we have meta-python in direct
        # dependencies
        computed_packages = self._find_minibuilds(self._packages)
        for package in computed_packages:
            if 'meta-python' in package.dependencies:
                pyversions.extend([ver for ver in PYTHON_VERSIONS])
                # if it is a egg, set the site-package to all python!
                if package.category == 'eggs':
                    selected_pyver[package.name] = PYTHON_VERSIONS
                stop = True

        if not stop:
            for package in packages:
                # we do not want eggs to make us build all site-packages,
                # always !
                if package.category != 'eggs' \
                   and not package.name.startswith('python') \
                   and not package.name.startswith('meta-python'):
                    # we want all versions of python:
                    if 'meta-python' in package.dependencies:
                        pyversions.extend([ver for ver in PYTHON_VERSIONS])
                    else:
                        # particular version selected ???
                        for pyversion in PYTHON_VERSIONS:
                            if 'python-%s' % pyversion in package.dependencies\
                               and not pyversion in pyversions:
                                pyversions.append(pyversion)

        if not pyversions:
            pyversions = PYTHON_VERSIONS
        # cut all python versions that are not needed.
        # for eggs, add site packages stuff only if if was not done.
        # Because we had maybe already set it if we install the egg as a direct
        # dependency and so we dont want to overwrite !
        selected_py = ['python-%s' % ver for ver in pyversions]
        for package in packages:
            if package.name.startswith('python') \
               and not package.name in selected_py:
                packages.pop(packages.index(package))
            if package.category == 'eggs'\
               and not package.name in self._packages:
                selected_pyver[package.name] = pyversions

        return packages, selected_pyver

    def _sync(self):
        # install our default minilays
        default_minilays = [s.strip() \
                            for s in self._config._sections\
                            .get('minimerge', {})\
                            .get('default_minilays','')\
                            .split('\n')]
        minimerge_section = self._config._sections.get('minimerge', {})
        urlbase = '%s/%s' % (
            minimerge_section\
            .get('minilays_url','')\
            .strip(),
            version
        )

        f = IFetcherFactory(self._config_path)
        hg = f(minimerge_section\
               .get('minilays_scm','')\
               .strip()
              )
        default_minilay_paths = ['%s/minilays/%s' % (self._prefix, minilay)\
                             for minilay in default_minilays]
        default_minilay_urls = ['%s/%s' % (urlbase, minilay)\
                                for minilay in default_minilays]
        for minilay, url in zip(default_minilay_paths, default_minilay_urls):
            hg.fetch_or_update(minilay, url)
        
        # for others minilays, we just try to update them
        for minilay in self._minilays:
            path = minilay.path
            type = None
            for strscm in ['hg', 'svn']:
                if os.path.isdir('%s/.%s' % (path, strscm)):
                    scm = f(strscm)
                    scm.update(dest=path)

