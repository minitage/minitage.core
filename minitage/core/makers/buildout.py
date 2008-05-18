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

import zc.buildout.buildout

from minitage.core.makers  import interfaces

class BuildoutError(interfaces.IMakerError):
    """General Buildout Error."""



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
        cwd = os.getcwd()
        os.chdir(directory)
        old_args = sys.argv[:]
        if not opts:
            opts = {}
        try:
            sys.argv[1:] = self.config.get('options',
                                           '-N -c  buildout.cfg -vvvvv').split()
            if opts.get('offline', False):
                sys.argv.append('-o')
            parts = opts.get('parts', False)
            if parts:
                sys.argv.append('install')
                if isinstance(parts, str):
                    sys.argv.extend(parts.split())
                else:
                    sys.argv.extend(parts)

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
        parts = None

        # if we install dependencies, we install in /part
        if minibuild.category == 'dependencies':
            parts = 'part'

        # if it s an egg, we must install just the needed
        # site-minibuilds if selected
        if minibuild.category == 'eggs':
            parts = ['site-packages-%s' % ver \
                     for ver in kwargs.get('python_versions', ())]

        if parts:
            options['parts'] = parts

        return options

# vim:set et sts=4 ts=4 tw=80:
