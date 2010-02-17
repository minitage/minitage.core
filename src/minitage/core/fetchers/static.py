# Copyright (C) 2009, Mathieu PASQUET <kiorky@cryptelium.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the <ORGANIZATION> nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.



__docformat__ = 'restructuredtext en'

import os
import urllib2
import shutil
import logging

from minitage.core.fetchers import interfaces
from minitage.core.unpackers.interfaces import IUnpackerFactory
import minitage.core.common

class StaticFetchError(interfaces.IFetcherError):
    """StaticFetchError."""


class StaticFetcher(interfaces.IFetcher):
    """ FILE/HTTP/HTTPS/FTP Fetcher.
    You can set a proxy with settings in the config :
    [minimerge]
    http_proxy = http://yourproxy:3128
    https_proxy = http://yourproxy:3128
    ftp_proxy = http://yourproxy:3128
    Example::
        >>> import minitage.core.fetchers.scm
        >>> http = scm.StaticFetcher()
        >>> http.fetch_or_update('http://uri/t.tbz2','/dir')
    """

    def __init__(self, config = None):

        if not config:
            config = {}

        self.logger = logging.getLogger('minitage.static.fetcher')
        interfaces.IFetcher.__init__(self, 'static', config = config)

    def update(self, dest, uri, opts=None, verbose=True):
        """Update a package.
        Arguments:
            - uri : check out/update uri
            - dest: destination to fetch to
            - opts : arguments for the fetcher

        """
        self.fetch(dest, uri, opts, verbose)

    def fetch(self, dest, uri, opts=None, verbose=True):
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
        filepath = os.path.join(download_dir, filename)
        md5path = os.path.join(download_dir, '%s.md5' % filename)

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
                        md5 = minitage.core.common.urlopen("%s.md5" % uri).read()
                        # maybe mark the file as already there
                        if os.path.exists(filepath):
                            self.logger.warning('File %s is already downloaded' % filepath)
                            if minitage.core.common.test_md5(filepath, md5):
                                self.logger.debug('MD5 has not changed, download is aborted.')
                                newer = False
                            else:
                                self.logger.debug(
                                    'Its md5 has changed: %s != %s, redownloading' % (
                                        minitage.core.common.md5sum(filepath), md5
                                    )
                                )
                except urllib2.HTTPError, e:
                    if e.code == 404:
                        self.logger.info('MD5 not found at %s, integrity will not be checked.' % "%s.md5" % uri)
                # handle file exc. as well
                except urllib2.URLError, e:
                    if e.reason.errno == 2:
                        self.logger.info('MD5 not found at %s, integrity will not be checked.' % "%s.md5" % uri)

                if newer:
                    if verbose:
                        self.logger.info('Downloading %s from %s.' % (filepath, uri))
                    data = minitage.core.common.urlopen(uri).read()
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
                message = 'Can\'t download file \'%s\' ' % filename
                message += 'from  \'%s\' .\n\t%s' % (uri, e)
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
                            shutil.copy(filepath, os.path.join(dest, filename))
                        if os.path.isdir(filepath):
                            shutil.copytree(filepath, os.path.join(dest, filename))
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
