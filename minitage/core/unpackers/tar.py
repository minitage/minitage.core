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
import tarfile

from minitage.core.unpackers import interfaces

class TarUnpacker(interfaces.IUnpacker):
    """Util to unpack a tar package to somewhere."""

    def __init__(self, config = None):
        self.config = config
        interfaces.IUnpacker.__init__(self, 'tar',  config)

    def unpack(self, filep, dest = './', opts=None):
        """Update a package.
        Exceptions:
            - InvalidUrlError
        Arguments:
            - filep: file to unpack
            - dest : destination folder.
            - opts : arguments for the unpacker
        """
        try:
            tar = tarfile.open(filep)
            if not os.path.isdir(dest):
                os.makedirs(dest)
            # use extract as extractall does not exist in python 2.4
            for tarinfo in tar:
                tar.extract(tarinfo, path=dest)
            tar.close()
        except Exception, e:
            message = 'Tar Unpack error\n\t%s' % e
            raise interfaces.UnpackerRuntimeError(message)

    def match(self, switch):
        """Test if the switch match the module."""
        if tarfile.is_tarfile(switch):
            return True
        return False

# vim:set et sts=4 ts=4 tw=80:
