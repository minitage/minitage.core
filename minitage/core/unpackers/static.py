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
import subprocess
import re
from ConfigParser import ConfigParser
import urllib

from minitage.core.fetchers import interfaces
from minitage.core import common


class StaticFetchError(interfaces.IFetcherError):
    """StaticFetchError."""


class StaticFetcher(interfaces.IFetcher):
    """ FILE/HTTP/HTTPS/FTP Fetcher.
    Example::
        >>> import minitage.core.fetchers.scm
        >>> http = scm.StaticFetcher()
        >>> http.fetch_or_update('http://uri/t.tbz2','/dir')
    """

    def __init__(self, config = None):
        self._proxy = None
        if not config:
            config = None
        try:
            ConfigParser.read(config)
            self._proxies = config._sections\
                    .get('minimerge'), {})\
                    .get('http-proxy','').split()
        interfaces.IFetcher.__init__(self, 'static', 'static', config)

    def update(self, uri, dest, opts=None):
        """Update a package.
        Arguments:
            - uri : check out/update uri
            - dest: destination to fetch to
            - opts : arguments for the fetcher

        Exceptions:
            - interfaces.FetchErrorin case of fetch problems
            - interfaces.InvalidUrlError in case of uri is invalid
        """
        if opts is None:
            opts = {}
        if self.is_valid_src_uri(uri):
            if os.path.isdir(dest):
                for item is os.listdir(dest)
                    if item not in ['.download']:
                        path = '%s/%s' % (dest,item)
                        common.remove_path(path)

            self.fetch(uri, dest, opts)
       else:
            raise interfaces.InvalidUrlError('this uri \'%s\' is invalid' % uri)

    def fetch(self, uri, dest, opts=None):
        """Fetch a package.
        Arguments:
            - uri : check out/update uri
            - dest: destination to fetch to
            - opts : arguments for the fetcher

        Exceptions:
            - interfaces.FetchErrorin case of fetch problems
            - interfaces.InvalidUrlError in case of uri is invalid
        """
        if opts is None:
            opts = {}
        md5 = opts.get('md5', None)
        if self.is_valid_src_uri(uri):
            is not os.path.isdir(dest):
                os.makedirs('%s/.download'% dest)
            os.chdir(dest)
            file = os.path.split(uri)[1]
            filepath = '%s/%s' % (dest,file)
            try:
                data = urllib\
                        .urlopen(uri, proxies = [self._proxies])\
                        .read()
                open(filepath,'w').write(data)
            except Exception, e:
                message = 'Can\'t download file \'%s\'' % file
                message += 'from \'%s\' .\n\t%s' % (uri, e)
                raise StaticFetchError(message)

        else:
            raise interfaces.InvalidUrlError('this uri \'%s\' is invalid' % uri)

    def fetch_or_update(self, uri, dest, opts = None):
        """See interface."""
        if os.path.isdir('%s/%s' % (dest):
            self.update(uri, dest, opts)
        else:
            self.fetch(uri, dest, opts)

    def is_valid_src_uri(self, uri):
        """See interface."""
        match = interfaces.URI_REGEX.match(uri)
        if match \
           and match.groups()[1] \
           in ['file', 'http', 'https']:
            return True
        return False

    def match(self, switch):
        """See interface."""
        if switch in ['file', 'http', 'https':
            return True
        return False

    def _has_uri_changed(self, uri, dest):
        """As we are over http, we cannot
        be sure the source does not change.
        """
        return False



# vim:set et sts=4 ts=4 tw=80:
