# coding=utf8

"""
Simple wrapper around Whoosh Index that presents a simpler interface.
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import os
import sys
import json
import time
from datetime import datetime

import pytz

import six
from six.moves import map

from whoosh.index import create_in, open_dir
from whoosh.query import Query
from whoosh.qparser import QueryParser
from whoosh.sorting import Facets

from knowhow.schema import SCHEMA, identifier
import knowhow.util as util
import knowhow.conf as conf


class Index(object):
    """
    Wrapper around a whoosh index with a simpler API for creating, updating,
    and searching the index.
    """

    def __init__(self, app_dir=None, index_dir=None):
        self.app_dir = app_dir or conf.get_app_dir()
        self.index_dir = index_dir or conf.get_data_dir(app_dir=self.app_dir)
        self._whoosh_index = None

    def open(self, clear=False):
        """
        Open this index and return the underlying whoosh index.

        If `clear` is true, then a new index is created, which replaces
        the existing index (and thus all existing data is lost).
        """
        exists = os.path.exists(self.index_dir)
        if not exists or clear:
            if not exists:
                os.makedirs(self.index_dir, mode=0o2755)
            self._whoosh_index = create_in(self.index_dir, SCHEMA)
        else:
            self._whoosh_index = open_dir(self.index_dir)
        return self._whoosh_index

    @property
    def _index(self):
        """
        The underlying whoosh index.
        """
        index = self._whoosh_index
        if index is None:
            index = self.open(clear=False)
        return index

    @staticmethod
    def _add(writer, **kwargs):
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
        kwargs = dict((k, util.decode(util.strip(kwargs[k]))) for k in kwargs)
        writer.update_document(**kwargs)

    def add(self, **kwargs):
        """
        Add document provided fields as kwargs.
        """
        assert 'text' not in kwargs
        with self._index.writer() as writer:
            Index._add(writer, **kwargs)

    def add_all(self, docs):
        """
        Add multiple documents using provided iterable of doc dicts.
        """
        with self._index.writer() as writer:
            for doc in docs:
                Index._add(writer, **doc)

    def remove(self, *ids):
        """
        Remove documents using provided identifiers.
        """
        num_removed = 0
        if ids:
            with self._index.writer() as writer:
                for id_ in ids:
                    num_removed += writer.delete_by_term('id', id_)
        return num_removed

    def parse(self, qs):  # pylint: disable=invalid-name
        """
        Parse given string query, returning a whoosh `Query`.
        """
        return QueryParser('text', self._index.schema).parse(qs)

    def search(self, query, **kw):  # pylint: disable=invalid-name
        """
        Search index using given query, passing `kw` to whoosh search.

        The `query` may be a query string or a query object.

        Returns a `knowhow.index.Search` object.
        """
        if not isinstance(query, Query):
            query = self.parse(query)
        return Search(self._index.searcher(), query, **kw)

    @staticmethod
    def _to_doc(docfields):
        doc = {}
        for key in docfields:
            value = docfields[key]
            key = util.decode(key)
            if isinstance(value, list):
                value = list(map(util.decode, value))
            else:
                value = util.decode(value)
            if key == 'tag' and not isinstance(value, list):
                value = [value]
            doc[key] = value
        return doc

    def __iter__(self):
        """
        Generator over all documents in index.
        """
        with self._index.reader() as reader:
            for _docnum, docfields in reader.iter_docs():
                yield Index._to_doc(docfields)

    def get_tags(self, prefix=None):
        """
        Get list of tags in this index.

        If `prefix` is not None, it should be a string that will be used
        to limit the tags returned to those that start with that prefix.
        """
        facets = Facets()
        facets.add_field('tag', allow_overlap=True)
        with self.search('*:*', groupedby=facets) as result:
            tags = list(result.groups().keys())
        if prefix:
            tags = [t for t in tags if t.startswith(prefix)]
        tags.sort()
        return tags

    def dump(self, fh):
        """
        Dump this index to given file handle as a JSON array, one doc per line.
        """
        # poor-man's json serialization, printing the enclosing container
        # manually and dumping each doc individually
        needs_ascii = util.needs_ascii(fh)
        fh.write('[')
        count = 0
        for doc in self:
            fh.write(',\n' if count else '\n')
            json.dump(doc, fh, default=util.json_serializer,
                      ensure_ascii=needs_ascii, sort_keys=True)
            count += 1
        fh.write('\n]')

    def pprint(self, fh=None):
        """
        Pretty-print all docs in this index to given file handle (or stdout).
        """
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
        """
        Load docs from file handle, expecting a JSON array of docs.
        """
        # 'fh' contains a JSON list of docs
        with self._index.writer() as writer:
            for doc in json.load(fh):
                doc = Index._to_doc(doc)
                if 'updated' in doc:
                    doc['updated'] = util.parse_datetime(doc['updated'])
                Index._add(writer, _no_update=True, **doc)

    def clear(self):
        """
        Clear this index, removing any existing documents.
        """
        self.open(clear=True)

    def last_modified(self, localize=False):
        """
        Get last modification date of this index as a datetime value.
        """
        dt = datetime.utcfromtimestamp(self._index.last_modified())
        if localize:
            # avoid using 'datetime.timezone', which is not available in py2
            epoch = time.mktime(dt.timetuple())
            offset = (datetime.fromtimestamp(epoch) -
                      datetime.utcfromtimestamp(epoch))
            dt = dt + offset
        return dt

    def __len__(self):
        """The number of documents in this index."""
        with self._index.reader() as reader:
            return reader.doc_count()


@six.python_2_unicode_compatible  # pylint: disable=too-few-public-methods
class Search(object):

    """
    A lazily-executed search against the underlying index.

    The search is performed upon `__enter__` (and the results are returned
    by that method), and index resources are released upon `__exit__`.
    """

    def __init__(self, searcher, query, **kw):
        assert searcher is not None
        assert query is not None
        self._searcher = searcher
        self._query = query
        self._kw = kw
        self._results = None

    def __enter__(self):
        self._searcher.__enter__()
        self._results = self._searcher.search(self._query, **self._kw)
        return Results(self._results, self)

    def __exit__(self, *exc_info):
        self._searcher.__exit__(*exc_info)

    def __repr__(self):
        return '<Search (query="%s")>' % str(self._query)

    __str__ = __repr__


@six.python_2_unicode_compatible  # pylint: disable=too-few-public-methods
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

    def __getitem__(self, n):  # pylint: disable=invalid-name
        return Result(self._results[n])

    def __iter__(self):
        return map(Result, self._results)

    def __bool__(self):  # PY3
        return bool(self._results)  # PY3

    def groups(self):
        """
        Get copy of groups dict for this results object.
        """
        return dict(self._results.groups())

    def __repr__(self):
        return '<Results (count=%d, search=%s)>' % (len(self), self._search)

    __str__ = __repr__

    if six.PY2:
        __nonzero__ = __bool__


@six.python_2_unicode_compatible
class Result(object):

    """ A single result of a search. """

    def __init__(self, hit):
        assert hit
        self._hit = hit

    @property
    def fields(self):
        """The fields for this result."""
        return self._hit.fields()

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

    __str__ = __repr__

    def get(self, field, default=None):
        """
        Get value of field, optionally using `default`.
        """
        return self.fields.get(field, default)
