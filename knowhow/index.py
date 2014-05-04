import os
import json
import pytz
from datetime import datetime

from whoosh.index import create_in, open_dir
from whoosh.query import Query
from whoosh.qparser import QueryParser

from knowhow.schema import SCHEMA, identifier
import knowhow.util as util


class Index:

    def __init__(self, app_dir=None, index_dir=None):
        if not app_dir:
            app_dir = util.get_app_dir()
        if not index_dir:
            index_dir = util.get_data_dir(app_dir=app_dir)
        self.app_dir = app_dir
        self.index_dir = index_dir
        self._ix = None

    def open(self, clear=False):
        exists = os.path.exists(self.index_dir)
        if not exists or clear:
            if not exists:
                os.makedirs(self.index_dir, mode=0o2755)
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

    def parse(self, qs):
        return QueryParser('content', self.ix.schema).parse(qs)

    def _search(self, q, **kw):
        assert isinstance(q, Query)
        return Search(self.ix.searcher(), q, **kw)

    def search(self, qs, **kw):
        return self._search(self.parse(qs), **kw)

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
                    json.dump(docfiles, fh, default=util.json_serializer)
                    count += 1
        finally:
            print('\n]', file=fh)

    def load(self, fh):
        with self.ix.writer() as writer:
            for doc in json.load(fh):
                doc['updated'] = util.parse_datetime(doc['updated'])
                self._add(writer, _no_update=True, **doc)

    def clear(self):
        self.open(clear=True)

    def __len__(self):
        with self.ix.reader() as reader:
            return reader.doc_count()


class Search:

    """
    A lazily-executed search against the underlying index.

    The search is performed upon `__enter__` (and the results are returned
    by that method), and index resources are released upon `__exit__`.
    """

    def __init__(self, searcher, q, **kw):
        assert searcher is not None
        assert q is not None
        self._searcher = searcher
        self._q = q
        self._kw = kw

    def __enter__(self):
        self._searcher.__enter__()
        self._results = self._searcher.search(self._q, **self._kw)
        return Results(self._results, self)

    def __exit__(self, *exc_info):
        self._searcher.__exit__(*exc_info)

    def __repr__(self):
        return '<Search (q=%r)>' % self._q


class Results:

    """
    The results of a `Search` operation, exposed as listlike object.
    """

    def __init__(self, results, search):
        assert results is not None
        assert search
        self._results = results
        self._search = search

    def __len__(self):
        return len(self._results)

    def __getitem__(self, n):
        return Result(self._results[n])

    def __iter__(self):
        return map(Result, self._results)

    def __bool__(self):
        return bool(self._results)

    def __repr__(self):
        return '<Results (count=%d, search=%r)>' % (len(self), self._search)


class Result:

    """ A single result of a search. """

    def __init__(self, hit):
        assert hit
        self._hit = hit

    @property
    def fields(self):
        return self._hit.fields()

    def __eq__(self, other):
        if not isinstance(other, Result):
            return False
        return self.fields == other.fields

    def __len__(self):
        return len(self.fields)

    def __iter__(self):
        return iter(self.fields)

    def __getitem__(self, field):
        return self.fields[field]

    def __contains__(self, key):
        return key in self.fields

    def __repr__(self):
        return '<Result (%s)>' % str(self.fields)

    def get(self, field, default=None):
        return self.fields.get(field, default)


def strip(val):
    if isinstance(val, str):
        return val.strip()
    try:
        return list(filter(None, map(strip, val)))
    except TypeError:
        return val
