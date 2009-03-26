"""
Generic Test case
"""
__docformat__ = 'restructuredtext'

import unittest
import doctest
import sys
import os
import tempfile
import shutil
import popen2
import subprocess
from os import makedirs as mkdir
from shutil import copy
import logging


logging.basicConfig()

current_dir = os.path.abspath(os.path.dirname(__file__))

def rmdir(*args):
    dirname = os.path.join(*args)
    if os.path.isdir(dirname):
        shutil.rmtree(dirname)

def sh(cmd, in_data=None):
    _cmd = cmd
    print cmd
    p = subprocess.Popen([_cmd], shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, close_fds=True)

    if in_data is not None:
        p.stdin.write(in_data)

    p.stdin.close()

    print p.stdout.read()

def ls(*args):
    dirname = os.path.join(*args)
    if os.path.isdir(dirname):
        filenames = os.listdir(dirname)
        for filename in sorted(filenames):
            print filename
    else:
        print 'No directory named %s' % dirname

def cd(*args):
    dirname = os.path.join(*args)
    os.chdir(dirname)

def config(filename):
    return os.path.join(current_dir, filename)


def cat(*args, **kwargs):
    filename = os.path.join(*args)
    if os.path.isfile(filename):
        data = open(filename).read()
        if kwargs.get('returndata', False):
           return data
        print data
    else:
        print 'No file named %s' % filename

def touch(*args, **kwargs):
    filename = os.path.join(*args)
    open(filename, 'w').write(kwargs.get('data',''))


#execdir = os.path.abspath(os.path.dirname(sys.executable))
tempdir = os.getenv('TEMP','/tmp')

def doc_suite(test_dir, setUp=None, tearDown=None, globs=None):
    """Returns a test suite, based on doctests found in /doctest."""
    suite = []
    tmpdir = tempfile.mkdtemp()
    if globs is None:
        globs = globals()
        globs['p'] = tmpdir

    flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE |
             doctest.REPORT_ONLY_FIRST_FAILURE)

    doctest_dir = test_dir

    # filtering files on extension
    docs = [os.path.join(doctest_dir, doc) for doc in
            os.listdir(doctest_dir) if doc.endswith('.txt')]

    for ftest in docs:
        test = doctest.DocFileSuite(ftest, optionflags=flags,
                                    globs=globs, setUp=setUp,
                                    tearDown=tearDown,
                                    module_relative=False)
        suite.append(test)

    return unittest.TestSuite(suite)

def test_suite():
    """returns the test suite"""
    return doc_suite(current_dir)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

