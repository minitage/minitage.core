#!/usr/bin/env python
__docformat__ = 'restructuredtext en'

import sys

from minitage.core.cli import get_minimerge
import traceback

def launch():
    try:
        minimerge = get_minimerge(read_options=True)
        minimerge.main()
    except Exception, e:
        trace = traceback.format_exc()
        sys.stderr.write('Minimerge executation failed:\n')
        if minimerge._debug:
            sys.stderr.write('\t%s\n' % trace)
        else:
            sys.stderr.write('\t%s\n' % e)
        sys.exit(-1)
# vim:set ft=python sts=4 ts=4 tw=80 et:
