__docformat__ = 'restructuredtext en'

import os
import sys
import optparse

from minitage.core import core
from minitage.core.common import (
    D, B, J,
    get_parser, get_install_root,
    first_run)


class Options(object):
    action = None
    ask = False
    delete = False
    generate_env = False
    install = False
    config = None
    debug = False
    fetchfirst = False
    fetchonly = False
    jump = False
    nodeps = False
    offline = False
    packages = []
    nofetch = False
    path = None
    pretend = False
    sync = False
    reinstall_minilays = False
    reinstall = False
    update = False
    upgrade = False
    verbose = True
    only_dependencies = False
    all_python_versions = False
    reinstall_minilays = False
    binary = False
    skip_self_upgrade = False

    def __init__(self, **kw):
        self.__dict__.update(**kw)


def do_read_options(read_options=False, **defaults):
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
    if not defaults:
        defaults = {}
    parser = get_parser()
    if read_options:
        (options, args) = parser.parse_args()
    else:
        options = Options()
        options.__dict__.update(defaults)
        args = []
    if (
        (options.reinstall and options.delete) or
        (options.fetchonly and options.offline) or
        (options.jump and options.nodeps)
    ):
        raise core.ConflictModesError('You are using conflicting modes')

    if (
        read_options
        and (
            (
                (not args and len(sys.argv) > 1)
                and not (options.sync or options.reinstall_minilays)
            )
        )
    ):
        message = 'You must precise which packages you want to deal with'
        raise core.NoPackagesError(message)

    actionsCount = 0
    if read_options:
        if len(sys.argv) == 1:
            print 'minimerge v%s' % parser.version
            parser.print_usage()
            print '\'%s --help\' for more inforamtion on usage.' % sys.argv[0]

        for action in [options.reinstall, options.install, options.delete]:
            if action:
                actionsCount = 1
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
        elif options.generate_env:
            options.action = 'generate_env'
        else:
            options.action = default_action
    if options.config:
        cfg = os.path.abspath(os.path.expanduser(options.config))
        if not os.path.isfile(cfg) and read_options:
            message = (
                'The configuration file specified does not exist: %s' % (
                    cfg))
            raise core.InvalidConfigFileError(message)
    else:
        cfg = os.path.join(get_install_root(), 'etc', 'minimerge.cfg')
    minimerge_options = {
        'action': options.action,
        'ask': options.ask,
        'config': cfg,
        'debug': options.debug,
        'fetchfirst': options.fetchfirst,
        'fetchonly': options.fetchonly,
        'jump': options.jump,
        'nodeps': options.nodeps,
        'offline': options.offline,
        'packages': args,
        'pretend': options.pretend,
        'update': options.update,
        'nofetch': options.nofetch,
        'upgrade': options.upgrade,
        'verbose': options.verbose,
        'only_dependencies': options.only_dependencies,
        'all_python_versions': options.all_python_versions,
        'reinstall_minilays': options.reinstall_minilays,
        'binary': options.binary,
        'skip_self_upgrade': options.skip_self_upgrade,
    }
    return minimerge_options


def get_minimerge(read_options=False, **kw):
    options = do_read_options(read_options=read_options, **kw)
    if not read_options:
        options['nolog'] = read_options
    test_first_run(options)
    return core.Minimerge(options)


def test_first_run(options):
    if not os.path.isfile(options['config']):
        options['first_run'] = True
        first_run()
