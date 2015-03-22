# coding=utf8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import os
import sys
import json
import pytz
from datetime import datetime

import six
from six.moves import map

from whoosh.index import create_in, open_dir
from whoosh.query import Query
from whoosh.qparser import QueryParser
from whoosh.sorting import Facets

from knowhow.schema import SCHEMA, identifier
import knowhow.util as util


class Index(object):
    """
    Wrapper around a whoosh index with a simpler API for creating, updating,
    and searching the index.
    """

    def __init__(self, app_dir=None, index_dir=None):
        self.app_dir = app_dir or util.get_app_dir()
        self.index_dir = index_dir or util.get_data_dir(app_dir=self.app_dir)
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
    def ix(self):
        if self._ix is not None:
            return self._ix
        return self.open(clear=False)

    def _add(self, writer, **kwargs):
        assert 'text' not in kwargs
        _no_update = kwargs.pop('_no_update', False)
        kwargs['id'] = identifier(kwargs)
        text = []
        if 'tag' in kwargs:
            text.extend(kwargs['tag'] * 4)
        if 'content' in kwargs:
            text.append(kwargs['content'])
        kwargs['text'] = ' '.join(text)
        if not _no_update:
            kwargs['updated'] = datetime.now(pytz.utc)
        kwargs = dict((k, util.decode(strip(kwargs[k]))) for k in kwargs)
        writer.update_document(**kwargs)

    def add(self, **kwargs):
        assert 'text' not in kwargs
        with self.ix.writer() as writer:
            self._add(writer, **kwargs)

    def add_all(self, docs):
        with self.ix.writer() as writer:
            for doc in docs:
                self._add(writer, **doc)

    def remove(self, *ids):
        num_removed = 0
        with self.ix.writer() as writer:
            for id_ in ids:
                num_removed += writer.delete_by_term('id', id_)
        return num_removed

    def parse(self, qs):
        return QueryParser('text', self.ix.schema).parse(qs)

    def _search(self, q, **kw):
        assert isinstance(q, Query)
        return Search(self.ix.searcher(), q, **kw)

    def search(self, qs, **kw):
        return self._search(self.parse(qs), **kw)

    def __iter__(self):
        with self.ix.reader() as reader:
            for docnum, docfiles in reader.iter_docs():
                doc = {}
                for k in docfiles:
                    v = docfiles[k]
                    if isinstance(k, six.binary_type):
                        k = k.decode('utf8')
                    if isinstance(v, six.binary_type):
                        v = v.decode('utf8')
                    elif isinstance(v, list):
                        v = [_v.decode('utf8')
                             if isinstance(_v, six.binary_type)
                             else _v for _v in v]
                    doc[k] = v
                yield doc

    def get_tags(self, prefix=None):
        facets = Facets()
        facets.add_field('tag', allow_overlap=True)
        with self.search('*:*', groupedby=facets) as result:
            tags = list(result.groups().keys())
        if prefix:
            tags = [t for t in tags if t.startswith(prefix)]
        tags.sort()
        return tags

    def dump(self, fh):
        # poor-man's json serialization, printing the enclosing container
        # manually and dumping each doc individually
        needs_ascii = util.needs_ascii(fh)
        fh.write('[')
        try:
            count = 0
            for doc in self:
                fh.write(',\n' if count else '\n')
                json.dump(doc, fh, default=util.json_serializer,
                          ensure_ascii=needs_ascii, sort_keys=True)
                count += 1
        finally:
            fh.write('\n]')

    def pprint(self, fh=None):
        if fh is None:
            fh = sys.stdout
        for doc in self:
            print('id:', doc['id'], file=fh)
            print('tag:', ', '.join(doc['tag']), file=fh)
            timestr = (util.utc_to_local(doc['updated'])
                           .strftime('%Y-%m-%d %H:%M:%S'))
            print('updated: %s' % timestr, file=fh)
            print(doc['content'], file=fh)
            print('\n', file=fh)

    def load(self, fh):
        # 'fh' contains a JSON list of docs; this whole JSON-based approach
        # that reads the entire list into memory in one shot wouldn't work for
        # very large indexes
        with self.ix.writer() as writer:
            for doc in json.load(fh):
                doc['updated'] = util.parse_datetime(doc['updated'])
                self._add(writer, _no_update=True, **doc)

    def clear(self):
        self.open(clear=True)

    def __len__(self):
        with self.ix.reader() as reader:
            return reader.doc_count()


@six.python_2_unicode_compatible
class Search(object):

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

    __str__ = __repr__


@six.python_2_unicode_compatible
class Results(object):

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

    def groups(self):
        return dict(self._results.groups())

    def __repr__(self):
        return '<Results (count=%d, search=%r)>' % (len(self), self._search)

    __str__ = __repr__


@six.python_2_unicode_compatible
class Result(object):

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
        return six.u('<Result (%s)>' % str(self.fields))

    __str__ = __repr__

    def get(self, field, default=None):
        return self.fields.get(field, default)


def strip(val):
    if isinstance(val, six.string_types):
        return val.strip()
    try:
        return list(filter(None, map(strip, val)))
    except TypeError:
        return val
