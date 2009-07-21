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
import sys
import ConfigParser
import logging
import logging.config
import copy
import shutil
from distutils.dir_util import copy_tree

from minitage.core import objects
from minitage.core.fetchers import interfaces as fetchers
from minitage.core.makers import interfaces as makers
from minitage.core.version import __version__

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


PYTHON_VERSIONS = ('2.4', '2.5', '2.6')

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
                - fetchfirst: if True, fetch all packages before building
                - offline: do not try to connect outside
                - nodeps: Squizzes all dependencies
                - action: what to do *mandatory*
                - sync: sync mode
                - config: configuration file path *mandatory*
                -flags :

                    - ask: prompt to continue
                    - pretend: do nothing that print what would be done.
                    - verbose: True to be verbose.
        """
        self.verbose = options.get('verbose', False)
        self._config_path = os.path.expanduser(options.get('config'))
        if not os.path.isfile(self._config_path):
            message = 'The config file is invalid: %s' % self._config_path
            raise InvalidConfigFileError(message)

        if not options.get('nolog', False):
            self._init_logging(self.verbose)

        if options is None:
            options = {}
        # first try to read the config in
        # - command line
        # - exec_prefix
        # - ~/.minimerge.cfg
        # We have the corresponding file allready filled in option._config, see
        # `minimerge.core.cli`
        #

        # read our config
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
        self._fetchfirst = options.get('fetchfirst', False)
        self._update = options.get('update', False)
        self._upgrade = options.get('upgrade', True)
        self._pretend = options.get('pretend', False)
        self._ask = options.get('ask', False)
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
        self._minilays = [objects.Minilay(
            path = os.path.expanduser(dir),
            minitage_config = copy.deepcopy(self._config)) \
            for dir in minilays_search_paths if os.path.isdir(dir)]

    def find_minibuild(self, package):
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

    def find_minibuilds(self, packages):
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

    def compute_dependencies(self, packages = None, ancestors = None):
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
        self.logger.debug('Will fetch package %s.' % (package.name))
        dest_container = '%s/%s' % (self._prefix, package.category)
        fetcherFactory = fetchers.IFetcherFactory(self._config_path)
        destination = '%s/%s' % (dest_container, package.name)
        # add maybe the scm to the path if it is avalaible
        fetcher = fetcherFactory(package.src_type)
        # in dependencies dir.
        #try to add scms merged via minitage to the path.
        deps = os.path.join(
            self.getPrefix(), 'dependencies')
        scm = getattr(fetcher, 'executable', None)
        if scm:
            # do we minimerged yet
            # and added a dependency directory?
            if os.path.exists(deps):
                for path in os.listdir(deps):
                    fp = os.path.join(
                        deps,
                        path,
                        'parts', 'part', 'bin')
                    if os.path.exists(
                        os.path.join(fp, scm)):
                        self.logger.debug(
                            'Adding %s to your path, this will '
                            'enable %s \'scm\'.' % (fp, scm)
                        )
                        os.environ['PATH'] = '%s%s%s' % (
                            fp, ':', os.environ['PATH']
                    )
        # add also minitage top /bin directory
        os.environ['PATH'] = '%s%s%s' % (
            os.path.join(self._prefix, 'bin'),
            ':',
            os.environ['PATH']
        )
        # create categ dir
        if not os.path.isdir(dest_container):
            os.makedirs(dest_container)
        if not os.path.exists(destination):
            self.logger.info('Fetching package %s from %s.' % (
                package.name,package.src_uri)
            )
            fetcher.fetch(
                destination,
                package.src_uri,
            )
        if self._update:
            self.logger.info('Updating package %s from %s.' % (
                package.name,package.src_uri)
            )

            if fetcher._has_uri_changed(destination, package.src_uri):
                temp = os.path.join(os.path.dirname(destination), 
                                    'minitage-checkout-tmp', 
                                    package.name)
                if os.path.isdir(temp):
                    shutil.rmtree(temp)
                fetcher.fetch(temp, package.src_uri) 
                copy_tree(temp, destination)
                shutil.rmtree(temp)
            else:
                fetcher.update(
                    destination,
                    package.src_uri,
            )  

    def _do_action(self, action, packages, pyvers = None):
        """Do action.
        Install, delete or reinstall a list of packages (minibuild instances).
        Arguments
            - action: reinstall|install|delete action to do.
            - packages: minibuilds to deal with in order!
            - pyvers: dict(package, [pythonver,]
        """
        if pyvers is None:
            pyvers = {}

        maker_kwargs = {}

        mf = makers.IMakerFactory(self._config_path)
        for package in packages:
            # if we are an egg, we maybe will have python versions setted.
            maker_kwargs['python_versions'] = pyvers.get(package.name, None)
            # we install unless we are dealing with a meta
            if not package.name.startswith('meta-'):
                options = {}

                # installation prefix
                ipath = self.get_install_path(package)

                # get the maker right for the install method
                maker = mf(package.install_method)

                # let our underlying maker make some addtionnnal choices for the
                # build options.
                options = maker.get_options(self, package, **maker_kwargs)

                # set offline and debug mode
                options['offline'] = self._offline
                options['debug'] = self._debug
                options['verbose'] = self.verbose

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
            m = self._find_minibuild(self._jump)
            if m:
                names = [package.name for package in packages]
                i = names.index(m.name)
                packages = packages[i:]
        except Exception, e:
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
            self.logger.debug('Calculating dependencies.')
            if not self._nodeps:
                packages = self._compute_dependencies(self._packages)
            else:
                packages = self._find_minibuilds(self._packages)

            if self._jump:
                # cut jumped dependencies.
                packages = self._cut_jumped_packages(packages)
                self.logger.debug('Shrinking packages away. _1/2_' )

            # cut pythons we do not need !
            # also get the parts to do in 'eggs' buildout
            pypackages, pyvers = self._select_pythons(packages[:])

            # do not take python tree in account if we are in nodep mode
            if not self._nodeps:
                packages = pypackages

            # cut jumped dependencies again.
            if self._jump:
                self.logger.debug('Shrinking packages away. _2/2_')
                packages = self._cut_jumped_packages(packages)

            self.logger.debug('Action:\t%s' % self._action)
            if packages:
                self.logger.debug('Packages:')
                for p in packages:
                    self.logger.debug('\t\t* %s' % p.name)

            stop = False
            answer = ''
            valid_answers = ('y', '', 'yes')
            if self._ask:
                print
                print 'Continue ? (y|n)'
                answer = raw_input()

            if self._pretend \
               or not answer.lower() in valid_answers:
                self.logger.info('Running in pretend mode or'
                                 ' user choosed to abort')
                stop = True

            if not stop:
                if answer:
                    self.logger.info('User choosed to continue')

                # fetch first, or just in time
                if self._fetchfirst:
                    # fetch all first, build after
                    for package in packages:
                        if not package.name.startswith('meta-'):
                            # fetch if not offline
                            if not (self._offline or self._action == 'delete'):
                                self._fetch(package)
                    # if we do not want just to fetch, let's go ,
                    # (install|delete|reinstall) baby.
                    if not self._fetchonly:
                        self._do_action(self._action, packages, pyvers)
                else:
                    # just in time fetch
                    for package in packages:
                        if not package.name.startswith('meta-'):
                            # fetch if not offline
                            if not (self._offline or self._action == 'delete'):
                                self._fetch(package)
                            # if we do not want just to fetch, let's go ,
                            if not self._fetchonly:
                                # (install|delete|reinstall) baby.
                                self._do_action(self._action, [package], pyvers)

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

               * If 'meta-python' is set in a direct dependency and the
                 dependency is an egg: we grab all versions

               * If a particular 'python-MAJOR.minor' is set in
                 the dependencies: we grab this version for selection.

               * if 'meta-python' is set on a dependency, we will use:

                       - an already installed python if any
                       - the most recent one otherwise

            - Next, when we have selected pythons, we will:

                * put our select pythons and their dependencies
                  at the top of the dep tree
                * delete others python and their dependencies
                  from the dependency tree.
                * map eggs and selected version for later use.

        Return
            - tuple with the according packages without uneeded stuff
              and a dict for the eggs with just the needed parts.
                ([new, packages, list], {'packagename': (buildout, parts)}
        """
        # select wich version of python are really needed.
        pyversions = []
        selected_pyver = {}
        metas = []
        pythons = [('python-%s' % version, version) \
                   for version in PYTHON_VERSIONS]
        ALL = False

        # look if we have eggs in direct dependencies,
        # if so: just build all site-packages available.
        direct_dependencies = self._find_minibuilds(self._packages)
        for package in direct_dependencies:
            if package.name in [python[0]\
                                for python in pythons]:
                pyversions.append(
                    package.name.replace('python-', '')
                )
            if package.category == 'eggs':
                pyversions.extend(PYTHON_VERSIONS)
                ALL = True
                break

        if not ALL:
            for package in packages:
                # first look if we have some python-ver in direct dependencies
                # and select them
                for python, version in pythons:
                    if python in package.dependencies \
                       and not package.name == 'meta-python':
                        if version not in pyversions:
                            pyversions.append(version)
                # if this is a meta or and egg, record it for later use
                if 'meta-python' in package.dependencies\
                   or package.category == 'eggs':
                    metas.append(package)

            # if we got meta packages but no particular python versions
            # on the run, we need to select the righ(s) versions to install
            if not pyversions:
                if metas:
                    # look if we hav allready installed pythons and select
                    # the first 'more recent' and exists
                    mostrecentpy = pythons[:]
                    mostrecentpy.reverse()
                    for python, version in mostrecentpy:
                        if os.path.exists(
                            os.path.join(
                                self._prefix,
                                'dependencies',
                                python
                            )):
                            if version not in pyversions:
                                pyversions.append(version)
                            break

                    # if we havent got any python version, and no python is
                    # already installed, we will need to merge one.
                    # eggs must have meta-python in their dependencies, so if we
                    # are building an egg which is not on direct dependencies.
                    # We will select at least the most recent python version
                    # there.
                    if not pyversions:
                        pyversions.append(pythons[:].pop()[1])

                # do nothing if we have no meta in dependencies and no python
                # too. python is not always a dependency :)
                else:
                    pass

        # change our real depedency tree according to local pythons
        # if we got meta or particular python versions.
        # get the dependencies for each python
        selected_pys = ['python-%s' % version for version in pyversions]
        python_deptree = self._compute_dependencies(selected_pys)

        # before inserting our new python deptree we will need to:
        #  - cut prior python dependencies if we have any
        #  - set python versions to build against for eggs.
        py_pn = [package.name for package in python_deptree]
        for package in packages[:]:
            # cut dependency if we need to cut it.
            # cut also not others python.
            if package.name in py_pn + [python[0] for python in pythons]:
                packages.pop(packages.index(package))
            if package.category == 'eggs':
                selected_pyver[package.name] = pyversions

        # insert our selected python(s) deptree at the top of our packages list
        python_deptree.reverse()
        for package in python_deptree:
            packages.insert(0, package)

        return packages, selected_pyver

    def _sync(self):
        """Sync or install our minilays."""
        # install our default minilays
        self.logger.info('Syncing minilays.')
        version = '.'.join( __version__.split('.')[:2])


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

        f = fetchers.IFetcherFactory(self._config_path)
        hg = f(minimerge_section\
               .get('minilays_scm','')\
               .strip()
              )

        # create default minilay dir in case
        if not os.path.isdir(os.path.join(self._prefix,'minilays')):
            os.makedirs(os.path.join(self._prefix,'minilays'))

        default_minilays_pathes_urls = [(os.path.join(
                                           self._prefix,
                                           'minilays',
                                           minilay),
                                           '/'.join((urlbase, minilay, '%s.tbz2' % minilay))
                                       )\
            for minilay in default_minilays]
        for d, url in default_minilays_pathes_urls:
            self.logger.info('Syncing %s from %s [via %s]' % (d, url, hg.name))
            if not os.path.exists(d):
                hg.fetch(d, url)
            else:
                hg.update(d, url)

        # for others minilays, we just try to update them
        for minilay in [m 
                        for m in self._minilays 
                        if not os.path.basename(m.path) in default_minilays]:
            path = minilay.path
            type = None
            # querying scm factory for registered scms
            # and removing static
            scms = [key for key in f.products.keys() if key != 'static']
            for strscm in scms:
                if os.path.isdir('%s/.%s' % (path, strscm)):
                    scm = f(strscm)
                    self.logger.info('Syncing %s from %s [via %s]' % ( path, scm.get_uri(path), strscm))
                    scm.update(dest=path, uri=scm.get_uri(path), verbose=self.verbose)

        self.logger.info('Syncing done.')

    def _init_logging(self, verbose=False):
        """Initialize logging system."""
        # configure logging system$
        try:
            logging.config.fileConfig(self._config_path)
        except:
            # just a stdout handler
            h = logging.StreamHandler()
            logging.root.addHandler(h)
        if self.verbose:
            logging.root.setLevel(0)
        else:
            logging.root.setLevel(logging.INFO)

        self.logger = logging.getLogger('minitage.core')
        self.logger.debug('(Re)Initializing minitage logging system.')


    def getUpgrade(self):
        """Accessor."""
        return self._upgrade

    def getPrefix(self):
        """Accessor."""
        return self._prefix

    def get_install_path(self, package):
        """Get a minibuild install path location."""
        # installation prefix
        return os.path.join(
            self._prefix,
            package.category,
            package.name
        )

    # api: do not break code
    _find_minibuilds = find_minibuilds
    _find_minibuild = find_minibuild
    _compute_dependencies = compute_dependencies
