#!/usr/bin/env python

"""Load previously dumped knowhow repo from stdin JSON array.

Usage:
  load.py
  load.py (-h | --help)
  load.py --version

Options:
  -h --help             Show this screen.
  --version             Show version.
"""
import sys

from docopt import docopt

import knowhow
from knowhow.index import Index


def main(args):
    Index().load(sys.stdin)
    return 0

if __name__ == '__main__':
    arguments = docopt(__doc__, version=knowhow.__version__)
    sys.exit(main(arguments))
