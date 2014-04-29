import os
import tempfile
from datetime import datetime

from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser

import knowhow
from knowhow.schema import SCHEMA, identifier


INDEX_DIR = os.path.join(tempfile.gettempdir(), knowhow.__name__)


class Index:

    def __init__(self, index_dir=INDEX_DIR):
        self.index_dir = index_dir
        self._ix = None

    @property
    def ix(self):
        if self._ix is not None:
            return self._ix
        if os.path.exists(self.index_dir):
            self._ix = open_dir(self.index_dir)
        else:
            os.mkdir(self.index_dir, mode=0o2755)
            self._ix = create_in(self.index_dir, SCHEMA)
        return self._ix

    def _add(self, writer, **kwargs):
        kwargs['id'] = identifier(kwargs)
        kwargs['updated'] = datetime.utcnow()
        writer.update_document(**strip(kwargs))

    def add(self, **kwargs):
        with self.ix.writer() as w:
            self._add(w, **kwargs)

    def add_all(self, docs):
        with self.ix.writer() as w:
            for doc in docs:
                self._add(w, **doc)

    def query(self, q):
        with self.ix.searcher() as s:
            result = s.search(q)
            print(len(result))
            return list(map(str, result))

    def search(self, qs):
        parser = QueryParser('content', self.ix.schema)
        return self.query(parser.parse(qs))


def strip(val):
    """
    Recursively strip whitespace from strings and arbitrarily nested
    strings in dicts or iterable containers, preserving all container types
    (e.g., tuples remain tuples in output, lists remain list in output,
    etc.). Any non-standard (non-dict) iterable types must have an
    `__init__` that accepts a list as the first parameter for creation
    of a new instance, just as `list` and `tuple` themselves do.
    """
    # Not very efficient, but it's nice to be able to preserve types;
    # of course, not needed above at all, since the values above
    # can only be lists that are not nested.
    if isinstance(val, str):
        return val.strip()
    elif isinstance(val, dict):
        return type(val)({k: strip(val[k]) for k in val})
    try:
        return type(val)(map(strip, val))
    except TypeError:  # not iterable
        return val     # everything else returned as is
