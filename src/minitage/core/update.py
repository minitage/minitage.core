#!/usr/bin/env python

# Copyright (C) 2009, Mathieu PASQUET <mpa@makina-corpus.com>
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
UPDATES = {}

def upperl(minitage):
    minitage.logger.info('Creating CPAN')
    for dir in (os.path.join(minitage._prefix, 'cpan', '5.8'),):
        if not os.path.exists(dir):
            os.makedirs(dir)
    # reinstall perl if any
    if os.path.exists(
        os.path.join(minitage._prefix,
                     'dependencies',
                     'perl-5.8'
                    )
    ):
        minitage.reinstall_packages(['perl-5.8'])

def reinstall_minilays(self):
    self.logger.info('Reinstallating minitage default minileys !')
    self.reinstall_minilays()

def updateHistory(self, force=False):
        """Copy the current minibuild prior to minimerge -s
        if minitage installation does not have any history yet"""
        hd = os.path.join(
            self._prefix, '.minitage_history'
        )
        if not os.path.exists(hd):
            force = True
        if force and not self.first_run:
            self.logger.info('Migrating existing and '
                             'installed packages to use the '
                             'minitage history system.')
            for minilay in self._minilays:
                minilay.load()
                for mb in minilay:
                    minibuild = minilay[mb]
                    if not minibuild.name.startswith('.'):
                        ip = self.get_install_path(minibuild)
                        if os.path.exists(ip):
                            if (not self.is_installed(minibuild)
                                and (len(os.listdir(ip))>0)):
                                self.set_package_mark(minibuild, 
                                                      'install', 
                                                      'install')
                                self.record_minibuild(minibuild)
            fic = open(hd, 'w')
            fic.write("")
            fic.close()
            self.logger.info('Migration complete, please restart minimerge.')
            self._action = None
            self._packages = []

def upgrademinilaysurl(self):
    pass

UPDATES['1.0.11'] = [#upperl,
                     reinstall_minilays]

UPDATES['2.0'] = [updateHistory,
                  reinstall_minilays,
                  ]

# vim:set et sts=4 ts=4 tw=80:
