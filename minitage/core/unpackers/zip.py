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

try:
    import zipfile
except:
    message = 'You must have python compiled with zlib support'
    raise interfaces.UnpackerRuntimeError(message)

from minitage.core.unpackers import interfaces

class ZipUnpacker(interfaces.IUnpacker):
    """Util to unpack a tar package to somewhere."""

    def __init__(self, config = None):
        self.config = config
        interfaces.IUnpacker.__init__(self, 'unzip', config)

    def unpack(self, file, dest = './', opts=None):
        """Update a package.
        Exceptions:
            - InvalidUrlError
        Arguments:
            - file: file to unpack
            - dest : destination folder.
            - opts : arguments for the unpacker
        """
        try:
            if not os.path.isdir(dest):
                os.makedirs(dest)
            zfobj = zipfile.ZipFile(file)
            for name in zfobj.namelist():
                if name.endswith('/'):
                    os.mkdir(os.path.join(dest, name))
                else:
                    # broken zip archives may contains 'dir/file' paths
                    # before 'dir' one
                    if len(name) > 1:
                        if '/' in name[1:] and not (name.endswith('/')): 
                            ldir = os.path.join(
                                dest,
                                '/'.join(name.split('/')[:-1])
                            )
                            if not os.path.exists(ldir):
                                os.makedirs(ldir)
                    outfile = open(os.path.join(dest, name), 'wb')
                    outfile.write(zfobj.read(name))
                    outfile.close()
        except Exception, e:
            message = 'Zip Unpack error\n\t%s' % e
            raise interfaces.UnpackerRuntimeError(message)

    def match(self, switch):
        """Test if the switch match the module."""
        if zipfile.is_zipfile(switch) or switch.endswith('.zip'):
            return True
        return False

# vim:set et sts=4 ts=4 tw=80:
