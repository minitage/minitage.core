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
import urllib
import shutil
import logging

from minitage.core.fetchers import interfaces
from minitage.core.unpackers.interfaces import IUnpackerFactory
import minitage.core.common


__log__ = logging.getLogger('minitage.static.fetcher')


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

        if not config:
            config = {}

        self.config = config
        self._proxies = config\
                .get('minimerge', {})\
                .get('http-proxies', '').split()
        if not self._proxies:
            self._proxies = None
        interfaces.IFetcher.__init__(self, 'static', config = config)

    def update(self, dest, uri, opts=None, verbose=False):
        """Update a package.
        Arguments:
            - uri : check out/update uri
            - dest: destination to fetch to
            - opts : arguments for the fetcher

        """
        # be conservative !!!
        # if os.path.isdir(dest):
        #     for item in os.listdir(dest):
        #         if item not in ['.download']:
        #             path = os.path.join(dest, item)
        #             minitage.core.common.remove_path(path)

        self.fetch(dest, uri, opts)

    def fetch(self, dest, uri, opts=None, verbose=False):
        """Fetch a package.
        Arguments:
            - uri : check out/update uri
            - dest: destination to fetch to
            - opts : arguments for the fetcher

        Exceptions:
            - interfaces.FetchError in case of fetch problems
            - interfaces.InvalidUrlError in case of uri is invalid
        """
        if opts is None:
            opts = {}
        md5 = opts.get('md5', None)

        download_dir = '%s/.download' % dest
        filename = os.path.split(uri)[1]
        filepath = '%s/%s' % (download_dir, filename)
        md5path = '%s/%s.md5' % (download_dir, filename)

        if not os.path.isdir(download_dir):
            os.makedirs(download_dir)

        # only download if we do not have already the file
        newer = True
        if (md5 and not minitage.core.common.test_md5(filepath, md5))\
           or not md5:
            try:
                # if we have not specified the md5, try to download one
                try:
                    if not md5:
                        md5 = urllib.urlopen(
                            "%s.md5" % uri, 
                            proxies = self._proxies).read().strip()
                        # maybe mark the file as already there
                        if os.path.exists(filepath):
                            __log__.debug('File %s is already downloaded' % filepath)
                            oo =  minitage.core.common.md5sum(filepath)
                            if minitage.core.common.test_md5(filepath, md5):
                                newer = False
                            else:
                                __log__.debug(
                                    'Its md5 has changed: %s != %s, redownloading' % (
                                        minitage.core.common.md5sum(filepath), md5
                                    )
                                )
                except:
                    pass
                if newer:
                    __log__.info('Downloading %s from %s.' % (filepath, uri))
                    data = urllib\
                            .urlopen(uri, proxies = self._proxies)\
                            .read()
                    # save the downloaded file
                    filep = open(filepath, 'wb')
                    filep.write(data)
                    filep.flush()
                    filep.close()
                    new_md5 = minitage.core.common.md5sum(filepath)
                    # regenerate the md5 file
                    md5p = open(md5path, 'wb')
                    md5p.write(new_md5)
                    md5p.flush()
                    md5p.close()

            except Exception, e:
                raise
                message = 'Can\'t download file \'%s\'' % filename
                message += 'from \'%s\' .\n\t%s' % (uri, e)
                raise StaticFetchError(message)

            if newer:
                try:
                    # try to unpack
                    f = IUnpackerFactory(self.config)
                    u = f(filepath)
                    if u:
                        u.unpack(filepath, dest)
                    # or move it to dest.
                    else:
                        if os.path.isfile(filepath):
                            shutil.copy(filepath, '%s/%s' % (dest, filename))
                        if os.path.isdir(filepath):
                            shutil.copytree(filepath, '%s/%s' % (dest, filename))
                except Exception, e:
                    message = 'Can\'t install file %s in its destination %s.'
                    raise StaticFetchError(message % (filepath, dest))

    def match(self, switch):
        """See interface."""
        if switch in ['static']:
            return True
        return False

    def _has_uri_changed(self, dest, uri):
        """As we are over static media, we cannot
        be sure the source does not change.
        """
        return False


    def is_valid_src_uri(self, uri):
        """Nothing to do there."""
        pass
# vim:set et sts=4 ts=4 tw=80:
