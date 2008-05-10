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

class InterfaceError(Exception): pass
class InvalidConfigForFactoryError(InterfaceError): pass
class NotImplementedMethodError(InterfaceError): pass
class InvalidComponentClassPathError(InterfaceError): pass
class InvalidComponentClassError(InterfaceError): pass

class IFactory(object):
    """Interface implementing the design pattern 'factory'
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
        self.name = name
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
                message = 'You must provide a [%s] section with appropriate content for this factory.'
                raise InvalidConfigForFactoryError(message % self.name)

        # for each class in the config File, try to instantiate and register
        # the type/plugin in the factory dict.
        self.registerDict(self.section)

    def registerDict(self, dict):
        """ for each item/class in the dict:
        Try to instantiate and register
        Arguments:
            - dict : dictionnary {item:class}
        Exceptions:
            - InvalidComponentClassPathError
        """
        # the type/plugin in the factory dict.
        for key in dict:
            try:
                # we have full.qualified.module.path.ClassName
                modules = dict[key].strip().split('.')
                klass_str = modules.pop()
                module = None
                # get the last inner submodule
                for submodule in modules:
                    if module:
                        file, path, desc = imp.find_module(submodule, module.__path__)
                        module = imp.load_module(submodule, file, path, desc)
                    else:
                        file, path, desc = imp.find_module(submodule)
                        module = imp.load_module(submodule, file, path, desc)

                # get now the corresponding class
                klass = getattr(module, klass_str)
            except Exception,e:
                raise InvalidComponentClassPathError('Invalid Component: \'%s/%s\'' % (key, dict[key]))
            self.register(key, klass)

    def register(self, type, klass):
        """register a possible product with it s factory
        Arguments
            - type: type to register
            - klass: klass the factory must intanciate
        """
        # little check that we have instance
        # XXX: find better.
        if not  isinstance(klass, str):
            self.products[type] = klass
        else:
            raise InvalidComponentClassError('Invalid Component: \'%s/%s\' does not point to a valid class.' % (type, klass))

    def __call__(self, switch):
        """possibly instanciate and return a product
        Implementation Exameple::
            for key in self.products:
                 klass = self.products[key]
                 instance = klass(self.sections.get(switch, {}))
                 if instance.match(switch):
                     return instance
        """
        raise NotImplementedMethodError('The method is not implemented')

class IProduct(object):
    """factory result"""

    def match(self, switch):
        """
        Arguments:
            - switch: parameter which will be used to know if the component can
            handle the request.
        Return:
            - boolean: wheither the product can be used.
        """
        raise NotImplementedMethodError('The method is not implemented')

# vim:set et sts=4 ts=4 tw=80:
