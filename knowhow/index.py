import os
import json
import pytz
import tempfile
from datetime import datetime

from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser

import knowhow
from knowhow.schema import SCHEMA, identifier
from knowhow.util import json_serializer, parse_datetime


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
        _no_update = kwargs.pop('_no_update', False)
        kwargs = {k: strip(kwargs[k]) for k in kwargs}
        kwargs['id'] = identifier(kwargs)
        if not _no_update:
            kwargs['updated'] = datetime.now(pytz.utc)
        writer.update_document(**kwargs)

    def add(self, **kwargs):
        with self.ix.writer() as w:
            self._add(w, **kwargs)

    def add_all(self, docs):
        with self.ix.writer() as w:
            for doc in docs:
                self._add(w, **doc)

    def query(self, q, **kw):
        with self.ix.searcher() as s:
            result = s.search(q, **kw)
            print(len(result))
            return list(map(str, result))

    def parse(self, qs):
        return QueryParser('content', self.ix.schema).parse(qs)

    def search(self, qs, **kw):
        return self.query(self.parse(qs), **kw)
        # parser = QueryParser('content', self.ix.schema)
        # return self.query(parser.parse(qs))

    def dump(self, fh):
        # poor-man's json serialization, printing the enclosing container
        # manually and dumping each doc individually; will have to take
        # another approach to deserializing if ever dealing with large indexes
        print('[', file=fh, end='')
        try:
            with self.ix.reader() as r:
                count = 0
                for docnum, docfiles in r.iter_docs():
                    print(',\n' if count else '\n', file=fh, end='')
                    json.dump(docfiles, fh, default=json_serializer)
                    count += 1
        finally:
            print('\n]', file=fh)

    def load(self, fh):
        with self.ix.writer() as w:
            for doc in json.load(fh):
                doc['updated'] = parse_datetime(doc['updated'])
                self._add(w, _no_update=True, **doc)


def strip(val):
    if isinstance(val, str):
        return val.strip()
    try:
        return list(filter(None, map(strip, val)))
    except TypeError:
        return val
