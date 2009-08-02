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



import logging
import sys
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

def reinstall_minilays(minitage):
    minitage.reinstall_minilays()

UPDATES['1.0.11'] = [#upperl, 
                     reinstall_minilays]

# vim:set et sts=4 ts=4 tw=80:
