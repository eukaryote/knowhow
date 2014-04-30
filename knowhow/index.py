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

    def open(self, clear=False):
        exists = os.path.exists(self.index_dir)
        if not exists or clear:
            if not exists:
                os.mkdir(self.index_dir, mode=0o2755)
            self._ix = create_in(self.index_dir, SCHEMA)
        else:
            self._ix = open_dir(self.index_dir)
        return self._ix

    @property
    def ix(self, clear=False):
        if self._ix is not None:
            return self._ix
        return self.open(clear=clear)

    def _add(self, writer, **kwargs):
        _no_update = kwargs.pop('_no_update', False)
        kwargs = {k: strip(kwargs[k]) for k in kwargs}
        kwargs['id'] = identifier(kwargs)
        if not _no_update:
            kwargs['updated'] = datetime.now(pytz.utc)
        writer.update_document(**kwargs)

    def add(self, **kwargs):
        with self.ix.writer() as writer:
            self._add(writer, **kwargs)

    def add_all(self, docs):
        with self.ix.writer() as writer:
            for doc in docs:
                self._add(writer, **doc)

    def query(self, q, **kw):
        with self.ix.searcher() as searcher:
            result = searcher.search(q, **kw)
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
            with self.ix.reader() as reader:
                count = 0
                for docnum, docfiles in reader.iter_docs():
                    print(',\n' if count else '\n', file=fh, end='')
                    json.dump(docfiles, fh, default=json_serializer)
                    count += 1
        finally:
            print('\n]', file=fh)

    def load(self, fh):
        with self.ix.writer() as writer:
            for doc in json.load(fh):
                doc['updated'] = parse_datetime(doc['updated'])
                self._add(writer, _no_update=True, **doc)

    def clear(self):
        self.open(clear=True)

    def __len__(self):
        with self.ix.reader() as reader:
            return reader.doc_count()


def strip(val):
    if isinstance(val, str):
        return val.strip()
    try:
        return list(filter(None, map(strip, val)))
    except TypeError:
        return val
