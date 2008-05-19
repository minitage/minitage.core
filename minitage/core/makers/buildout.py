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
import sys
import logging

import zc.buildout.buildout

from minitage.core.makers  import interfaces

class BuildoutError(interfaces.IMakerError):
    """General Buildout Error."""

__logger__ = 'minitage.makers.buildout'

class BuildoutMaker(interfaces.IMaker):
    """Buildout Maker.
    """
    def __init__(self, config = None):
        """Init a buildout maker object.
        Arguments
            - config keys:

                - options: cli args for buildout
        """
        if not config:
            config = {}
        self.logger = logging.getLogger(__logger__)
        self.config = config
        interfaces.IMaker.__init__(self)

    def match(self, switch):
        """See interface."""
        if switch == 'buildout':
            return True
        return False

    def reinstall(self, directory, opts=None):
        """Rebuild a package.
        Warning this will erase .installed.cfg forcing buildout to rebuild.
        Problem is that underlying recipes must know how to handle the part
        directory to be already there.
        This will be fine for minitage recipes in there. But maybe that will
        need boiler plate for other recipes.
        Exceptions
            - ReinstallError
        Arguments
            - directory : directory where the packge is
            - opts : arguments for the maker
        """
        os.remove('%s/.installed.cfg' % directory)
        self.install(directory, opts)

    def install(self, directory, opts=None):
        """Make a package.
        Exceptions
            - MakeError
        Arguments
            - dir : directory where the packge is
            - opts : arguments for the maker
        """
        self.logger.info('Running buildout in %s' % directory)
        cwd = os.getcwd()
        os.chdir(directory)
        old_args = sys.argv[:]
        if not opts:
            opts = {}
        try:
            sys.argv[1:] = self.config.get('options',
                                           '-N -c  buildout.cfg -vvvvv').split()
            if opts.get('offline', False):
                self.logger.info('We will run in offline mode!')
                sys.argv.append('-o')
            parts = opts.get('parts', False)
            if parts:
                sys.argv.append('install')
                if isinstance(parts, str):
                    sys.argv.extend(parts.split())
                else:
                    sys.argv.extend(parts)

            # monkey patch
            # to avoid double logging
            def donothing(self):
                self._logger = logging.getLogger(__logger__)
                verbosity = 0
                level = self['buildout']['log-level']
                if level in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
                    level = getattr(logging, level)
                else:
                    try:
                        level = int(level)
                    except ValueError:
                        self._error("Invalid logging level %s", level)
                        verbosity = self['buildout'].get('verbosity', 0)
                try:
                    verbosity = int(verbosity)
                except ValueError:
                    self._error("Invalid verbosity %s", verbosity)

                level -= verbosity
                self._log_level = level
            zc.buildout.buildout.Buildout._setup_logging = donothing

            zc.buildout.buildout.main()
        except Exception, instance:
            sys.argv = old_args
            os.chdir(cwd)
            raise BuildoutError('Buildout failed: :\n\t%s' % instance)
        sys.argv = old_args
        os.chdir(cwd)

    def get_options(self, minimerge, minibuild, **kwargs):
        """Get python options according to the minibuild and minimerge instance.
        For eggs buildouts, we need to know which versions of python we
        will build site-packages for
        For parts, we force to install only the 'part' buildout part.
        Arguments
            - minimerge a minitage.core.Minimerge instance
            - minibuild a minitage.core.object.Minibuild instance
            - kwargs:

                - 'python_versions' : list of major.minor versions of
                  python to compile against.
        """
        options = {}
        parts = []

        # if it s an egg, we must install just the needed
        # site-minibuilds if selected
        if minibuild.category == 'eggs':
            parts = ['site-packages-%s' % ver \
                     for ver in kwargs.get('python_versions', ())]

        options['parts'] = parts

        return options

# vim:set et sts=4 ts=4 tw=80:
