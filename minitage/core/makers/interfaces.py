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

class IMakerError(Exception): pass
class MakeError(IMakerError): pass
class DeleteError(IMakerError): pass
class ReinstallError(IMakerError): pass

class IMakerFactory(interfaces.IFactory):
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
        """return a maker
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
    """Interface for making a package from somewhere"
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

    def delete(self, dir, opts=None):
        """delete a package
        Exceptions:
            - DeleteError
        Arguments:
            - dir : directory where the packge is
            - opts : arguments for the maker
        """
        if os.path.isdir(dir):
            try:
                shutil.rmtree(dir)
            except:
                raise DeleteError('Cannot remove \'%s\'' % dir)

    def reinstall(self, dir, opts):
        """rebuild a package
        Exceptions:
            - ReinstallError
        Arguments:
            - dir : directory where the packge is
            - opts : arguments for the maker
        """
        raise interfaces.NotImplementedMethodError('The method is not implemented')

    def make(self, dir, ops=None):
        """make a package
        Exceptions:
            - MakeError
        Arguments:
            - dir : directory where the packge is
            - opts : arguments for the maker
        """
        raise interfaces.NotImplementedMethodError('The method is not implemented')

    def match(self, switch):
        raise interfaces.NotImplementedMethodError('The method is not implemented')

# vim:set et sts=4 ts=4 tw=80:
