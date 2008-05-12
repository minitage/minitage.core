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

import re
import os
import subprocess
import shutil

from minitage.core import interfaces

class IUnpackerError(Exception):
    """General Unpacker Error."""


class UnpackError(IUnpackerError):
    """Unpack Error."""


class UnpackerRuntimeError(IUnpackerError):
    """Unknown runtime Error."""


class IUnpackerFactory(interfaces.IFactory):
    """Interface Factory."""

    def __init__(self, config=None):
        """
        Arguments:
            - config: a configuration file with a self.name section
                    containing all needed classes.
        """

        interfaces.IFactory.__init__(self, 'unpackers', config)
        self.registerDict(
            {
                'tar': 'minitage.core.unpackers.tar.TarUnpacker',
                'zip': 'minitage.core.unpackers.zip.ZipUnpacker',
            }
        )

    def __call__(self, switch):
        """return a unpacker
        Arguments:
            - switch: archive absolute path
              Default ones:

                -tar: tar|gz|bz2
                -zip: zip
        """
        for key in self.products:
            klass = self.products[key]
            instance = klass(config = self.section)
            if instance.match(switch):
                return instance

class IUnpacker(interfaces.IProduct):
    """Interface for unpacking a package to somewhere.
    Basics
         To register a new unpacker to the factory you ll have 2 choices:
             - Indicate something in a config.ini file and give it to the
               instance initialization.
               Example::
                   [unpackers]
                   type=mymodule.mysubmodule.MyUnpackerClass

             - register it manually with the .. function::register
               Example::
                   >>> klass = getattr(module,'superklass')
                   >>> factory.register('tar', klass)

    What a unpacker needs, to be a unpacker
        Locally, the methods in the interfaces ;)
        Basically, it must implement
            - unpack to unpack the source
    """

    def __init__(self, name, config = None):
        """
        Attributes:
            - name : name of the unpacker
            - executable : path to the executable. Either absolute or local.
        """
        self.name = name
        if not config:
            config = {}
        self.config = config

    def unpack(self, file, dest, opts=None):
        """Update a package.
        Exceptions:
            - InvalidUrlError
        Arguments:
            - file: file to unpack
            - dest : destination folder.
            - opts : arguments for the unpacker
        """
        raise interfaces.NotImplementedError('The method is not implemented')

    def match(self, switch):
        """Test if the switch match the module.
        switch is there an absolute pathname"""
        raise interfaces.NotImplementedError('The method is not implemented')

    def _unpack_cmd(self, command):
        """Helper to run unpack commands."""
        p = subprocess.Popen('%s %s 2>&1' % (self.executable, command),
                             shell = True, stdout=subprocess.PIPE)
        ret = p.wait()
        if ret != 0:
            message = '%s failed to achieve correctly.' % self.name
            raise UnpackerRuntimmeError(message)

# vim:set et sts=4 ts=4 tw=80:
