# Copyright (C)2008 'Mathieu PASQUET <kiorky@cryptelium.net>'
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

import os
import sys
import optparse

from minitage.core import core


usage = """
%(arg)s [Options] minibuildn  \t\t\t: Installs  package(s)
%(arg)s [Options] -j m  a b m ... n  \t\t: Installs  package(s) from 'm' to 'n'
%(arg)s [Options] -rm minibuild ... minibuildn  \t: Uninstall package(s)
%(arg)s [Options] -uU minibuild ... minibuildn  \t: Update/Upgrade package(s)
%(arg)s [Options] -RuU minibuild ... minibuildn  \t: Update/Upgrade/rebuild package(s)
""" % {'arg': sys.argv[0]}


def do_read_options():
    """Parse the command line thought arguments
       and throws CliError if any error.
    Returns
        - `options` : the options to give to minimerge
            They are cli parsed but action [string] is added to the oject.
            action can be one of these :

                - install
                - delete
                - reinstall
        - `args` [list] : cli left args, in fact these are the packages to deal with.
    """

    default_action = 'install'
    path = sys.exec_prefix

    offline_help = 'Build offline, do not try to connect outside.'
    debug_help = 'Run in debug mode'
    jump_help = 'Squizze prior dependencies to the '\
                'minibuild specified in that option'
    fetchonly_help = 'Fetch the packages but do not build yet'
    fetchfirst_help = 'Fetch the packages first before building them'
    delete_help = 'Remove selected packages'
    reinstall_help = 'Unconditionnaly rebuild/reinstall packages'
    install_help = 'Installs packages (default action)'
    nodeps_help = 'Squizzes all dependencies'
    config_help = 'Alternate config file. By default it\'s searched in '\
                  '%s/etc/minimerge.cfg.' % sys.exec_prefix
    pretend_help = 'Do nothing, show what will be done'
    update_help = 'Update packages from where they come '\
            'prior to compilation step automaticly'
    ask_help = 'Do nothing, show what will be done and ask to continue'
    upgrade_help = 'Will try to rebuild already installed sofware. if '\
            'you need to be sure that all will be rebuilt, activate '\
            'also the -R flag. If you want minimerge to update '\
            'the packages from where they come, please activate '\
            'also the -U flag.'

    option_list = [
        optparse.make_option('-c', '--config',
                             action='store', dest='config',
                             help = config_help),
        optparse.make_option('-d', '--debug',
                             action='store_true', dest='debug',
                             help = debug_help),
        optparse.make_option('-o', '--offline',
                             action='store_true', dest='offline',
                             help = offline_help),
        optparse.make_option('-s', '--sync',
                             action='store_true', dest='sync',
                             help = nodeps_help),
        optparse.make_option('-F', '--fetchonly',
                             action='store_true', dest='fetchonly',
                             help = fetchonly_help),
         optparse.make_option('-f', '--fetchfirst',
                             action='store_true', dest='fetchfirst',
                             help = fetchfirst_help),
        optparse.make_option('-i', '--install',
                             action='store_true', dest='install',
                             help = install_help),
        optparse.make_option('-U', '--update',
                             action='store_true', dest='update',
                             help = update_help),
        optparse.make_option('-u', '--upgrade',
                             action='store_true', dest='upgrade',
                             help = upgrade_help),
        optparse.make_option('-R', '--reinstall',
                             action='store_true', dest='reinstall',
                             help = reinstall_help),
        optparse.make_option('--rm',
                             action='store_true', dest='delete',
                             help = delete_help),
        optparse.make_option('-N', '--nodeps',
                             action='store_true', dest='nodeps',
                             help = nodeps_help),
        optparse.make_option('-j', '--jump',
                             action='store', dest='jump',
                             help = jump_help),
        optparse.make_option('-p', '--pretend',
                             action='store_true', dest='pretend',
                             help = pretend_help),
        optparse.make_option('-a', '--ask',
                             action='store_true', dest='ask',
                             help = ask_help),
        optparse.make_option('-v', '--verbose',
                             action='store_true', dest='verbose',
                             help = 'Be verbose.'),
    ]
    parser = optparse.OptionParser(version=core.__version__,
                                   usage=usage,
                                   option_list=option_list)
    (options, args) = parser.parse_args()

    if (options.reinstall and options.delete) or\
       (options.fetchonly and options.offline) or \
       (options.jump and options.nodeps):
        raise core.ConflictModesError('You are using conflicting modes')

    if (not args and len(sys.argv) > 1) and not options.sync:
        message = 'You must precise which packages you want to deal with'
        raise core.NoPackagesError(message)

    if len(sys.argv) == 1:
        print 'minimerge v%s' % parser.version
        parser.print_usage()
        print '\'%s --help\' for more inforamtion on usage.' % sys.argv[0]

    actionsCount = 0
    for action in [options.reinstall, options.install, options.delete]:
        if action:
            actionsCount += 1
    if actionsCount > 1:
        message = 'You must precise only one action at a time'
        raise core.TooMuchActionsError(message)

    if options.delete:
        options.action = 'delete'
    elif options.reinstall:
        options.action = 'reinstall'
    elif options.sync:
        options.action = 'sync'
    elif options.install:
        options.action = 'install'
    else:
        options.action = default_action

    if not options.config:
        for file in ['~/.minimerge.cfg', '%s/etc/minimerge.cfg' % path]:
            file = os.path.expanduser(file)
            if os.path.isfile(file):
                options.config = file
                break

    # be sure to be with full path object.
    if not options.config:
        message = 'The configuration file specified does not exist'
        raise core.InvalidConfigFileError(message)
    if not os.path.isfile(options.config):
        message = 'The configuration file specified does not exist'
        raise core.InvalidConfigFileError(message)
    options.config = os.path.expanduser(options.config)

    minimerge_options = {
        'action': options.action,
        'ask': options.ask,
        'config': options.config,
        'debug': options.debug,
        'fetchfirst': options.fetchfirst,
        'fetchonly': options.fetchonly,
        'jump': options.jump,
        'nodeps': options.nodeps,
        'offline': options.offline,
        'packages': args,
        'path': path,
        'pretend': options.pretend,
        'update': options.update,
        'upgrade': options.upgrade,
        'verbose': options.verbose,
    }
    return minimerge_options

