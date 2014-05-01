#!/usr/bin/env python

"""Show information about the `knowhow` index.

Usage:
  info.py
  info.py (-h | --help)
  info.py --version

Options:
  -h --help             Show this screen.
  --version             Show version.
"""

import sys

from docopt import docopt

import knowhow
from knowhow.index import Index


def print_info(reader):
    print('%d snippet(s)' % reader.doc_count())
    tags = (t.decode('utf-8') for t in reader.lexicon('tag'))
    print('all tags:', ', '.join(tags))
    print('most frequent tags:')
    for count, term in reader.most_frequent_terms('tag'):
        print('    {0}: {1}'.format(count, term))


def main(args):
    with Index().ix.reader() as reader:
        print_info(reader)
    return 0


if __name__ == '__main__':
    arguments = docopt(__doc__, version=knowhow.__version__)
    sys.exit(main(arguments))
