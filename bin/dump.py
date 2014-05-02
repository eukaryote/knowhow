#!/usr/bin/env python

"""Dump knowhow repo to stdout as JSON array.

Usage:
  dump.py
  dump.py (-h | --help)
  dump.py --version

Options:
  -h --help             Show this screen.
  --version             Show version.
"""
import sys

from docopt import docopt

import knowhow
from knowhow.index import Index


def main(args):
    Index().dump(sys.stdout)
    return 0

if __name__ == '__main__':
    arguments = docopt(__doc__, version=knowhow.__version__)
    sys.exit(main(arguments))
