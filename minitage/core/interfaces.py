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

import ConfigParser
import imp
import types
import pkg_resources

class InterfaceError(Exception):
    """General Interface Error."""


class InvalidConfigForFactoryError(InterfaceError):
    """Invalid config file Error."""


class NotImplementedError(InterfaceError):
    """Method is not implemented in the child class."""


class InvalidComponentClassPathError(InterfaceError):
    """Component class path was not found."""


class InvalidComponentClassError(InterfaceError):
    """Component Class is not valid."""


class IFactory(object):
    """Interface implementing the design pattern 'factory'.
    Basics
        To register a new fetcher to the factory you ll have 2 choices:
            - Indicate something in a config.ini file and give it to the
              instance initialization.
              Example::
                    [fetchers]
                    type=mymodule.mysubmodule.MyFetcherClass

            - register it manually with the .. function::register
              Example::
                >>> factory.register('svn', 'module.fetchcher.NiceSvnFetcher')

    Attributes
    - products : dictionary:
        { src_type : IFetcher instance}

    """

    def __init__(self, name, config=None):
        """
        Arguments:
            - config: a configuration file with a self.name section
                    containing all needed classes.
        """
        self.name = 'minitage.%s' % name
        self.config = ConfigParser.ConfigParser()
        self.section = {}
        self.sections = {}
        self.products = {}
        if config:
            try:
                self.config.read(config)
                self.sections = self.config._sections
                for section in self.sections:
                    del self.sections[section]['__name__']
                self.section = self.config._sections[self.name]
            except KeyError, e:
                message = 'You must provide a [%s] section with '
                message += 'appropriate content for this factory.'
                raise InvalidConfigForFactoryError(message % self.name)

        # for each class in the config File, try to instantiate and register
        # the type/plugin in the factory dict.
        self.registerDict(self.section)

    def registerDict(self, dict):
        """For each item/class in the dict:
        Try to instantiate and register.
        Arguments:
            - dict : dictionnary {item:class}
        Exceptions:
            - InvalidComponentClassPathError
        """
        # the type/plugin in the factory dict.
        #
        for key in dict:
            try:
                smodule, sklass = dict[key].strip().split(':')
                module = __import__(smodule, None, None, [''])
                klass = getattr(module, sklass)
            except Exception,e:
                 message = 'Invalid Component: \'%s/%s\'' % (key, dict[key])
                 raise InvalidComponentClassPathError(message)
            self.register(key, klass)

    def register(self, type, klass):
        """Register a product with its factory.
        Arguments
            - type: type to register
            - klass: klass the factory must intanciate
        """
        # little check that we have instance
        # XXX: find better.
        if not  isinstance(klass, str):
            self.products[type] = klass
        else:
            message = 'Invalid Component: \'%s/%s\' ' % (type, klass)
            message += 'does not point to a valid class.'
            raise InvalidComponentClassError()

    def __call__(self, switch):
        """Possibly instanciate and return a product.
        Implementation Exameple::
            for key in self.products:
                 klass = self.products[key]
                 instance = klass(self.sections.get(switch, {}))
                 if instance.match(switch):
                     return instance
        """
        raise NotImplementedError('The method is not implemented')

class IProduct(object):
    """factory result"""

    def match(self, switch):
        """Select the product if match.
        Arguments:
            - switch: parameter which will be used to know if the component can
            handle the request.
        Return:
            - boolean: wheither the product can be used.
        """
        raise NotImplementedError('The method is not implemented')

# vim:set et sts=4 ts=4 tw=80:
