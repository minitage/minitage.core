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

from minitage.core.makers import interfaces

class BuildoutError(interfaces.IMakerError): pass

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

    def match(self, switch):
        """See interface."""
        if switch == 'buildout':
            return True
        return False

    def reinstall(self, dir, opts=None):
        """Rebuild a package.
        Warning this will erase .installed.cfg forcing buildout to rebuild.
        Problem is that underlying recipes must know how to handle the part
        directory to be already there.
        This will be fine for minitage recipes in there. But maybe that will
        need boiler plate for other recipes.
        Exceptions
            - ReinstallError
        Arguments
            - dir : directory where the packge is
            - opts : arguments for the maker
        """
        os.remove('%s/.installed.cfg' % dir)
        self.make(dir, opts)

    def make(self, dir, opts=None):
        """Make a package.
        Exceptions
            - MakeError
        Arguments
            - dir : directory where the packge is
            - opts : arguments for the maker
        """
        cwd = os.getcwd()
        os.chdir(dir)
        old_args = sys.argv[:]
        if not opts:
            opts = {}
        try:
            sys.argv[1:] = self.config.get('options',
                                           '-c -N buildout.cfg -vvvvv').split()
            if opts.get('offline',False):            
                sys.argv.append('-o')
            zc.buildout.buildout.main()
        except Exception, e:
            raise BuildoutError('Buildout failed: :\n\t%s' % e)
        os.chdir(cwd)

# vim:set et sts=4 ts=4 tw=80:
