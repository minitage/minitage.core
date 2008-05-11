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
import shutil

from minitage.core import interfaces

class IMakerError(Exception):
    """General Maker Error."""


class MakeError(IMakerError):
    """Make runtime error."""


class DeleteError(IMakerError):
    """Delete runtime error."""


class ReinstallError(IMakerError):
    """Reinstall runtime error."""



class IMakerFactory(interfaces.IFactory):
    """Factory for makers utilities."""

    def __init__(self, config=None):
        """
        Arguments:
            - config: a configuration file with a self.name section
                    containing all needed classes.
        """

        interfaces.IFactory.__init__(self, 'makers', config)
        self.registerDict(
            {
                'buildout': 'minitage.core.makers.buildout.BuildoutMaker',
            }
        )

    def __call__(self, switch):
        """Return a maker.
        Arguments:
            - switch: maker type
              Default ones:

                -buildout: buildout
        """
        for key in self.products:
            klass = self.products[key]
            instance = klass(self.sections.get(switch, {}))
            if instance.match(switch):
                return instance


class IMaker(interfaces.IProduct):
    """Interface for making a package from somewhere.
    Basics
         To register a new maker to the factory you ll have 2 choices:
             - Indicate something in a config.ini file and give it to the
               instance initialization.
               Example::
                   [makers]
                   type=mymodule.mysubmodule.MyMakerClass

             - register it manually with the .. function::register
               Example::
                   >>> klass = getattr(module,'superklass')
                   >>> factory.register('svn', klass)

    What a maker needs to be a maker
        Locally, the methods in the interfaces ;)
        Basically, it must implement
            - make, delete, reinstall, match
    """

    def delete(self, directory, opts=None):
        """Delete a package.
        Exceptions:
            - DeleteError
        Arguments:
            - dir : directory where the packge is
            - opts : arguments for the maker
        """
        if os.path.isdir(directory):
            try:
                shutil.rmtree(directory)
            except:
                raise DeleteError('Cannot remove \'%s\'' % directory)

    def reinstall(self, directory, opts):
        """Rebuild a package.
        Exceptions:
            - ReinstallError
        Arguments:
            - directory : directory where the packge is
            - opts : arguments for the maker
        """
        raise interfaces.NotImplementedError('The method is not implemented')

    def install(self, directory, ops=None):
        """Make a package.
        Exceptions:
            - MakeError
        Arguments:
            - dir : directory where the packge is
            - opts : arguments for the maker
        """
        raise interfaces.NotImplementedError('The method is not implemented')

    def match(self, switch):
        """Return true if the product match the switch."""
        raise interfaces.NotImplementedError('The method is not implemented')


    def get_options(self, minimerge, minibuild, **kwargs):
        """Return a dict of needed options
        according to a minibuild and a minimerge instance and for the other
        packages to be built in the session."""
        raise interfaces.NotImplementedError('The method is not implemented')

# vim:set et sts=4 ts=4 tw=80:
