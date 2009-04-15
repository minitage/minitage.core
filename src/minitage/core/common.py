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

import logging
import md5
import os
import re
import sys
import shutil
import tempfile
import urllib2
import urlparse
import subprocess

from pkg_resources import Requirement, resource_filename
from minitage.core.version import __version__

class MinimergeError(Exception): pass

def splitstrip(l, token=None):
    """Split a list and return non stripped elements."""
    return [elem \
            for elem in l.split(token) \
            if elem.strip()]

def md5sum(filep):
    """Return the md5 sium of a file"""
    fobj = open(filep,'rb')
    m = md5.new()
    while True:
        d = fobj.read(8096)
        if not d:
            break
        m.update(d)
    return m.hexdigest()

def test_md5(filep, md5sum_ref):
    """Test if file match md5 md5sum."""
    if md5sum(filep) == md5sum_ref:
        return True

    return False


def remove_path(path):
    """Remove a path."""
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)

def append_env_var(env, var, sep=":", before=True):
    """Append text to a environnement variable.
    @param env String variable to set
    @param before append before or after the variable
    """
    for path in var:
        if before:
            os.environ[env] = "%s%s%s" % (
                path, sep, os.environ.get(env, '')
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

def system(c, log=None):
    """Execute a command."""
    if log:
        log.info("Running %s" % c)
    ret = os.system(c)
    if ret:
        raise SystemError('Failed', c)
    return ret

def Popen(command, verbose=False):
    # FIXME: Popen strange behaviour
    ret = os.system(command)
    #stdout = None
    #if not verbose:
    #    stdout = subprocess.PIPE
    # p = subprocess.Popen(command,
    #                      shell=True,
    #                      stdin=subprocess.PIPE,
    #                      stdout = stdout,
    #                      stderr=subprocess.PIPE,
    #                     )
    # ret = p.wait()
    if ret != 0:
        error = ''
        #if not verbose:
        #    error = p.stdout.read()
        message = '%s\n%s' % (error,
                            '----------------------------------------------------------\n'
                            '\'%s\' failed!\n'
                            '\tPlease report all the above backtrace along\n'
                            '\t with your bug report.\n'
                            '----------------------------------------------------------\n' % (command)
                           )
        raise MinimergeError(message)

def get_from_cache(url,
                   download_cache = None,
                   logger = None,
                   file_md5 = None,
                   offline = False):
    """Get a file from the buildout download cache.
    Arguments:
        - url : where to fetch from
        - name: filename destination
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
    if not logger:
        logger = logging.getLogger(filename)

    # get the file from the right place
    fname = tmp2 = file_present = ''
    if download_cache:
        # if we have a cache, try and use it
        logger.debug(
            'Searching cache at %s' % download_cache)
        if os.path.isdir(download_cache):
            # just cache files for now
            fname = os.path.join(download_cache, filename)

    # do not download if we have the file
    file_present = os.path.exists(fname)
    if file_present:
        logger.debug(
            'Using cache file in %s' % fname
        )
    else:
        logger.debug(
            'Did not find %s under cache: %s' % (
                filename,
                download_cache)
        )
    if os.path.exists(url):
        url = 'file://%s' % os.path.abspath(url)

    if not file_present:
        # static local files
        if offline and not (('file://' in url) or (os.path.exists(url))):
            # no file in the cache, but we are staying offline
            raise MinimergeError(
                "Offline mode: file from %s not found in the cache at %s" %
                (url, download_cache)
            )

        try:
            # okay, we've got to download now
            tmp2 = None
            if download_cache:
                # set up the cache and download into it
                fname = os.path.join(download_cache, filename)
                logger.debug(
                    'Cache download %s as %s' % (
                        url,
                        download_cache)
                )
            else:
                # use tempfile
                tmp2 = tempfile.mkdtemp('buildout-' + filename)
                fname = os.path.join(tmp2, filename)
            logger.info(
                'Downloading %s in %s' % (url,fname)
            )
            open(fname,'w').write(urllib2.urlopen(url).read())
            if file_md5:
                if not test_md5(fname, file_md5):
                    raise MinimergeError(
                        'MD5SUM mismatch for %s: Good:%s != Bad:%s' % (
                            fname,
                            file_md5,
                            md5sum(fname)
                        )
                    )

        except Exception, e:
            if tmp2 is not None:
                shutil.rmtree(tmp2)
            if download_cache:
                os.remove(fname)
            raise MinimergeError(
                'Failed download for %s:\t%s' % (url, e)
            )

    return fname

def first_run():
    ## first time create default config !
    prefix = os.path.abspath(sys.exec_prefix)
    config = os.path.join(prefix, 'etc', 'minimerge.cfg')
    mm_version = __version__
    if not os.path.isfile(config):
        print """\n\n
====================================================
\t\tWELCOME TO THE MINITAGE WORLD
====================================================

You seem to be running minitage for the first time.

\t* Creating some default stuff...
\t* Generating default config: %s """ % config
        print '\t* Creating minilays dir'
        for dir in (os.path.split(config)[0],
                    os.path.join(sys.exec_prefix, 'minilays'),
                    os.path.join(sys.exec_prefix, 'logs'),
                    os.path.join(sys.exec_prefix, 'eggs', 'cache'),
                    os.path.join(sys.exec_prefix, 'eggs', 'develop-cache'),
                   ):
            if not os.path.isdir(dir):
                os.makedirs(dir)
        tconfig = resource_filename(Requirement.parse(
            'minitage.core == %s' % mm_version),
            'etc/minimerge.cfg')
        changelog= resource_filename(Requirement.parse(
            'minitage.core == %s' % mm_version),
            'share/minitage/CHANGES.txt')
        readme= resource_filename(Requirement.parse(
            'minitage.core == %s' % mm_version),
            'share/minitage/README.txt')
        prefixed = re.sub('%PREFIX%',prefix, open(tconfig,'r').read())
        fic = open(config, 'w')
        fic.write(prefixed)
        fic.flush()
        fic.close()
        print '\n\n'

def which(program, environ=None, key = 'PATH', split = ':'):
    if not environ:
        environ = os.environ
    PATH=environ.get(key, '').split(split)
    fp = None
    if '/' in program:
        fp = os.path.abspath(program)
    if not fp:
        for entry in PATH:
            fp = os.path.abspath(os.path.join(entry, program))
            if os.path.exists(fp):
                break
    if os.path.exists(fp):
        return fp
    raise IOError('Program not fond: %s in %s ' % (program, PATH))


def search_latest(regex, minilays):
    for mpath, directories, files in os.walk(minilays):
        subpath = mpath.replace(
            os.path.commonprefix([minilays, mpath]),
            '')
        if subpath and (not subpath.count(os.path.sep) > 1):
            files.sort()
            files.reverse()
            for minibuild in files:
                if not minibuild.startswith('.'):
                    if re.match(regex, minibuild, re.M|re.S|re.U):
                        return minibuild
    raise Exception('Regex %s didnt match or '
                    'minibuild not found in %s.' % (regex, minilays))

# vim:set et sts=4 ts=4 tw=80:
