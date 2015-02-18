from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from os.path import exists, join
import json

from knowhow.index import Index

import tests


def test_index_open_nonexistent_noclear(tmp_app_index_dir_paths):
    tmpd, appd, indexd = tmp_app_index_dir_paths
    index = Index(app_dir=appd, index_dir=indexd)
    assert not exists(indexd)
    index.open(clear=False)
    assert exists(indexd)


def test_index_open_nonexistent_clear(tmp_app_index_dir_paths):
    tmpd, appd, indexd = tmp_app_index_dir_paths
    index = Index(app_dir=appd, index_dir=indexd)
    assert not exists(indexd)
    index.open(clear=True)
    assert exists(indexd)


def test_index_open_noclear(index_one):
    assert len(index_one) == 1
    index_one.open(clear=False)
    assert len(index_one) == 1


def test_index_open_clear(index_one):
    assert len(index_one) == 1
    index_one.open(clear=True)
    assert len(index_one) == 0


def test_index_search_tag(index_one):
    with index_one.search('tag:mytag0') as results:
        assert len(results) == 1
        assert results[0].get('content') == 'mycontent0'


def test_index_search_content(index_one):
    with index_one.search('content:mycontent0') as results:
        assert len(results) == 1
        assert results[0].get('tag') == 'mytag0'


def test_index_search_boolean(index_one):
    with index_one.search('content:mycontent0 AND tag:mytag0') as results:
        assert len(results) == 1
        assert results[0].get('tag') == 'mytag0'


def test_index_add(index_one):
    assert len(index_one) == 1
    with index_one.search('tag:mytag1') as results:
        assert len(results) == 0
    index_one.add(**tests.test_doc1)
    assert len(index_one) == 2
    with index_one.search('tag:mytag1') as results:
        assert len(results) == 1


def test_index_dump_empty(tmpd, index_empty):
    path = join(tmpd, 'dump.json')
    with open(path, 'wb') as f:
        index_empty.dump(f)
    with open(path) as f:
        docs = json.load(f)
    assert len(docs) == 0


def test_index_dump_one(tmpd, index_one):
    path = join(tmpd, 'dump.json')
    with open(path, 'wb') as f:
        index_one.dump(f)
    with open(path) as f:
        docs = json.load(f)
    assert len(docs) == 1
    doc = docs[0]
    assert doc['tag'] == 'mytag0'
    assert doc['content'] == 'mycontent0'


def test_index_load(tmpd, index_empty):
    path = join(tmpd, 'load.json')
    with open(path, 'w') as f:
        json.dump([tests.test_doc_dumped], f)
    assert len(index_empty) == 0
    with open(path, 'r') as f:
        index_empty.load(f)
    assert len(index_empty) == 1
    with index_empty.search('tag:mytag') as results:
        assert len(results) == 1
        assert results[0].get('content') == tests.test_doc_dumped['content']
