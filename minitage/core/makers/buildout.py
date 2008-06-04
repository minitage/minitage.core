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
import logging


from minitage.core.makers  import interfaces
import minitage.core.core
import minitage.core.common

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
        mypath = os.path.join(
            directory,
            '.installed.cfg'
        )
        if os.path.exists(mypath):
            os.remove(mypath)
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
        if not opts:
            opts = {}
        try:
            argv = self.config.get('options',
                                           ' -vvvvv').split()
            if opts.get('offline', False):
                self.logger.info('Buildout is running in offline mode!')
                argv.append('-o')
            if opts.get('debug', False):
                self.logger.info('Buildout is running in debug mode!')
                argv.append('-D')
            parts = opts.get('parts', False)
            if isinstance(parts, str):
                parts = parts.split()


            # Try to upgrade only if we need to
            # (we chech only when we have a .installed.cfg file
            installed_cfg = os.path.join(directory, '.installed.cfg')
            if not opts.get('upgrade', True)\
               and os.path.exists(installed_cfg):
                self.logger.debug('Buildout will not run in %s'
                            ' as there is a .installed.cfg file'
                            ' indicating us that the software is already'
                            ' installed but minimerge is running in'
                            ' no-update mode. If you want to try'
                            ' to update/rebuild it unconditionnaly,'
                            ' please relaunch with -uUR.' % directory)
                return


            # running buildout in our internal way
            if not os.path.exists(
                os.path.join(
                    directory,
                    'bin',
                    'buildout')):
                minitage.core.common.system(
                    'buildout bootstrap',
                    self.logger
                )
            if parts:
                for part in parts:
                    self.logger.info('Installing single part: %s' % part)
                    minitage.core.common.system(
                        './bin/buildout %s install %s ' % (
                            ' '.join(argv),
                            part
                        ),
                        self.logger
                    )
            else:
                self.logger.info('Installing parts')
                minitage.core.common.system(
                    './bin/buildout %s ' % (
                        ' '.join(argv),
                    ),
                    self.logger
                )
        except Exception, instance:
            os.chdir(cwd)
            raise BuildoutError('Buildout failed: :\n\t%s' % instance)
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
        if kwargs is None:
            kwargs = {}

        # if it s an egg, we must install just the needed
        # site-packages if selected
        if minibuild.category == 'eggs':
            vers = kwargs.get('python_versions', None)
            if not vers:
                vers = minitage.core.core.PYTHON_VERSIONS
            parts = ['site-packages-%s' % ver for ver in vers]

        options['parts'] = parts

        # prevent buildout from running if we have already installed stuff
        # and do not want to upgrade.
        options['upgrade'] = minimerge.getUpgrade()

        return options

# vim:set et sts=4 ts=4 tw=80:
