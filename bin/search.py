#!/usr/bin/env python

"""Search knowhow for entries matching tags and/or content keywords.

Usage:
  search.py [-t TAG|--tag=TAG] [KEYWORD]...
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
    tag_query, keyword_query = None, None
    if args.get('--tag'):
        tags = [s.strip() for s in args['--tag'].split(',')]
        terms = [Term('tag', s) for s in tags if s]
        if terms:
            tag_query = And(terms)
    index = Index()
    if args.get('KEYWORD'):
        keyword_query = index.parse(' '.join(kw for kw in args['KEYWORD']))
    if keyword_query:
        results = index.query(keyword_query, filter=tag_query)
    else:
        assert tag_query  # at least one should have been required by docopt
        results = index.query(tag_query)
    for doc in results:
        print(doc)
    return 0


if __name__ == '__main__':
    arguments = docopt(__doc__, version=knowhow.__version__)
    sys.exit(main(arguments))
