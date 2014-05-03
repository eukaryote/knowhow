#!/usr/bin/env python

"""Show information about the knowhow index.

Usage:
  info.py
  info.py (-h | --help)
  info.py --version

Options:
  -h --help             Show this screen.
  --version             Show version.
"""

import sys
from datetime import datetime, timezone

from docopt import docopt

import knowhow
from knowhow.index import Index


def print_overview(index):
    ix = index.ix
    utc_dt = datetime.utcfromtimestamp(ix.last_modified())
    local_dt = utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
    print('Index:', ix.storage.folder)
    print('Last updated:', local_dt)
    print('Repo size: %d snippet(s)' % ix.doc_count())
    print()


def print_details(index):
    with index.ix.reader() as reader:
        tags = (t.decode('utf-8') for t in reader.lexicon('tag'))
        print('tags:', ', '.join(tags))
        print('most frequent tags:')
        for count, term in reader.most_frequent_terms('tag'):
            print('  {0}: {1}'.format(int(count), term.decode('utf-8')))


def main(args):
    index = Index()
    print_overview(index)
    print_details(index)
    return 0


if __name__ == '__main__':
    arguments = docopt(__doc__, version=knowhow.__version__)
    sys.exit(main(arguments))
