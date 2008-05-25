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
import distutils

import zc.buildout.buildout

from minitage.core.makers  import interfaces
import minitage.core.core

class BuildoutError(interfaces.IMakerError):
    """General Buildout Error."""

__logger__ = 'minitage.makers.buildout'

### monkey patches for zc.buildout avoiding it to stop minitage logging :)
def donothing(self):
    """buildout.Buildout logging."""
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



def main(args=None):
    """buildout.main function without logging stuff."""
    if args is None:
        args = sys.argv[1:]

    config_file = 'buildout.cfg'
    verbosity = 0
    options = []
    windows_restart = False
    user_defaults = True
    debug = False
    while args:
        if args[0][0] == '-':
            op = orig_op = args.pop(0)
            op = op[1:]
            while op and op[0] in 'vqhWUoOnND':
                if op[0] == 'v':
                    verbosity += 10
                elif op[0] == 'q':
                    verbosity -= 10
                elif op[0] == 'W':
                    windows_restart = True
                elif op[0] == 'U':
                    user_defaults = False
                elif op[0] == 'o':
                    options.append(('buildout', 'offline', 'true'))
                elif op[0] == 'O':
                    options.append(('buildout', 'offline', 'false'))
                elif op[0] == 'n':
                    options.append(('buildout', 'newest', 'true'))
                elif op[0] == 'N':
                    options.append(('buildout', 'newest', 'false'))
                elif op[0] == 'D':
                    debug = True
                else:
                    _help()
                op = op[1:]

            if op[:1] in  ('c', 't'):
                op_ = op[:1]
                op = op[1:]

                if op_ == 'c':
                    if op:
                        config_file = op
                    else:
                        if args:
                            config_file = args.pop(0)
                        else:
                            _error("No file name specified for option", orig_op)
                elif op_ == 't':
                    try:
                        timeout = int(args.pop(0))
                    except IndexError:
                        _error("No timeout value specified for option", orig_op)
                    except ValueError:
                        _error("No timeout value must be numeric", orig_op)

                    import socket
                    print 'Setting socket time out to %d seconds' % timeout
                    socket.setdefaulttimeout(timeout)

            elif op:
                if orig_op == '--help':
                    _help()
                _error("Invalid option", '-'+op[0])
        elif '=' in args[0]:
            option, value = args.pop(0).split('=', 1)
            if len(option.split(':')) != 2:
                _error('Invalid option:', option)
            section, option = option.split(':')
            options.append((section.strip(), option.strip(), value.strip()))
        else:
            # We've run out of command-line options and option assignnemnts
            # The rest should be commands, so we'll stop here
            break

    if verbosity:
        options.append(('buildout', 'verbosity', str(verbosity)))

    if args:
        command = args.pop(0)
        if command not in (
            'install', 'bootstrap', 'runsetup', 'setup', 'init',
            ):
            _error('invalid command:', command)
    else:
        command = 'install'

    try:
        try:
            buildout = zc.buildout.buildout.Buildout(config_file, options,
                                user_defaults, windows_restart, command)
            getattr(buildout, command)(args)
        except SystemExit:
            pass
        except Exception, v:
            zc.buildout.buildout._doing()
            if debug:
                exc_info = sys.exc_info()
                import pdb, traceback
                traceback.print_exception(*exc_info)
                sys.stderr.write('\nStarting pdb:\n')
                pdb.post_mortem(exc_info[2])
            else:
                if isinstance(v, (zc.buildout.UserError,
                                  distutils.errors.DistutilsError,
                                  )
                              ):
                    _error(str(v))
                else:
                    zc.buildout.buildout._internal_error(v)

    finally:
        # only change is there, we do nothing,
        # we DO NOT SHUT DOWN LOGGING SYSTEM !
        pass

 


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
            
            # apply monkey patches
            zc.buildout.buildout.Buildout._setup_logging = donothing
            zc.buildout.buildout.main  = main

            # running buildout in our internal way
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

        return options

# vim:set et sts=4 ts=4 tw=80:
