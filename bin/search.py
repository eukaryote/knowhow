#!/usr/bin/env python

"""Search knowhow.

Usage:
  search.py [-t TAG|--tag=TAG]
  search.py (-h | --help)
  search.py --version

Options:
  -h --help           Show this screen.
  --version           Show version.
  -t TAG, --tag=TAG   Search for snippets tagged with TAG.
"""
import sys
from docopt import docopt

import knowhow
from knowhow.index import Index
from whoosh.query import And, Term


def main(args):
    if args.get('--tag'):
        tags = [s.strip() for s in args['--tag'].split(',')]
        terms = [Term('tag', t) for t in tags if t]
        print('terms:', terms)
        for doc in Index().query(And(terms)):
            print(doc)
    return 0


if __name__ == '__main__':
    arguments = docopt(__doc__, version=knowhow.__version__)
    sys.exit(main(arguments))
