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

"""
helpers functions
"""
import datetime
import logging
import md5
import os
import re
import setuptools.archive_util
import sha
import shutil
import sys
import tempfile
import urllib2
import urlparse

from minitage.core import core

def test_md5(file, md5sum):
    """Test if file match md5 md5sum."""
    fobj = open(file,'rb')
    m = md5.new()
    while True:
        d = fobj.read(8096)
        if not d:
            break
        m.update(d)
    if m.hexdigest() == md5sum:
        return True

    return False


def remove_path(path):
    """Remove a path."""
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)

def append_env_var(env, var ,sep=":", before=True):
    """Append text to a environnement variable.
    @param env String variable to set
    @param before append before or after the variable
    """
    for path in var:
        if before:
            os.environ[env] = "%s%s%s" % (
                path,sep,os.environ.get(env, '')
            )
        else:
            os.environ[env] = "%s%s%s" % (
                os.environ.get(env, ''), sep, path
            )

def substitute(filename, search_re, replacement):
    """Substitutes text within the contents of ``filename`` matching
    ``search_re`` with ``replacement``.
    """
    search = re.compile(search_re, re.MULTILINE)
    text = open(filename).read()
    text = replacement.join(search.split(text))
    newfilename = '%s%s' % (filename, '.~new')
    newfile = open(newfilename, 'w')
    newfile.write(text)
    newfile.close()
    shutil.copymode(filename, newfilename)
    shutil.move(newfilename, filename)

def system(c,log=None):
    if log:
        log.info("Running %s" % c)
    if os.system(c):
        raise SystemError('Failed', c)

def get_from_cache(url, name,
                   download_cache = None,
                   md5 = None,
                   offline = False):
    """Get a file from the buildout download cache.
    Arguments:
        - url : where to fetch from
        - download_cache: path to the dl cache
        - install_from_cache:
        - offline : offline mode
    """
    # borrowed from zc.recipe.cmmi
    if download_cache:
        if not os.path.isdir(download_cache):
            os.makedirs(download_cache)

    _, _, urlpath, _, _ = urlparse.urlsplit(url)
    filename = urlpath.split('/')[-1]

    # get the file from the right place
    fname = tmp2 = file_present = None
    if download_cache:
        # if we have a cache, try and use it
        logging.getLogger(name).debug(
            'Searching cache at %s' % download_cache)
        if os.path.isdir(download_cache):
            # just cache files for now
            fname = os.path.join(download_cache, filename)
            file_present=os.path.exists(fname)
            if file_present:
                logging.getLogger(name).debug(
                    'Using cache file in %s' % fname
                )
            else:
                logging.getLogger(name).debug(
                    'Did not find %s under cache: %s' % (
                        filename,
                        download_cache)
                )

    if not file_present:
        if offline:
            # no file in the cache, but we are staying offline
            raise core.MinimergeError(
                "Offline mode: file from %s not found in the cache at %s" %
                (url, download_cache)
            )

        try:
            # okay, we've got to download now
            tmp2 = None
            if download_cache:
                # set up the cache and download into it
                fname = os.path.join(download_cache, filename)
                logging.getLogger(name).debug(
                    'Cache download %s as %s' % (
                        url,
                        download_cache)
                )
            else:
                # use tempfile
                tmp2 = tempfile.mkdtemp('buildout-' + name)
                fname = os.path.join(tmp2, filename)
            logging.getLogger(name).info(
                'Downloading %s in %s' % (url,fname)
            )
            open(fname,'w').write(urllib2.urlopen(url).read())
            if md5:
                if not test_md5(fname, md5):
                    raise core.MinimergeError(
                        'MD5SUM mismatch for %s' % fname
                    )

        except Exception, e:
            if tmp2 is not None:
               shutil.rmtree(tmp2)
            if download_cache:
               shutil.rmtree(fname)
            raise core.MinimergeError(
                'Failed download for %s:\t%s' % (url, e)
            )

    return fname
# vim:set et sts=4 ts=4 tw=80:
