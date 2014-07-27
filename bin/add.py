#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""Add (or update) a knowhow entry, optionally with one or more tags.

Usage:
  add.py [-t TAG|--tag=TAG] TERM...
  add.py (-h | --help)
  add.py --version

Options:
  -h --help             Show this screen.
  --version             Show version.
  -t TAG, --tag=<TAG>   Add TERM values and associate with TAG.
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import sys

from docopt import docopt

import knowhow
from knowhow.index import Index


def parse(val):
    if val is not None:
        tokens = (s.strip() for s in val.split(','))
        return filter(None, tokens)


def main(args):
    Index().add(
        tag=list(parse(args['--tag'])),
        content=' '.join(filter(None, args['TERM']))
    )
    return 0


if __name__ == '__main__':
    arguments = docopt(__doc__, version=knowhow.__version__)
    sys.exit(main(arguments))
