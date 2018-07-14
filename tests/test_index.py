# coding=utf8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import datetime
import hashlib
import json
from os.path import abspath, dirname, exists, join
import pickle

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from pytz import UTC

from knowhow.index import Index, Results
from knowhow import schema, util
from knowhow.conf import PYTHON2

import tests


def test_index_to_doc_tag_str():
    doc = {"id": "myid", "tag": "mytag", "content": "my content"}
    result = Index._to_doc(doc)
    assert result == {"id": doc["id"], "tag": [doc["tag"]], "content": doc["content"]}


def test_index_to_doc_tag_list():
    doc = {"id": "myid", "tag": ["tag1", "tag2"], "content": "my content"}
    assert Index._to_doc(doc) == doc


def test_index_property_opens_without_clearing(tmp_app_index_dir_paths):
    _, appd, indexd = tmp_app_index_dir_paths
    index1 = Index(app_dir=appd, index_dir=indexd)
    with index1._index.reader() as reader:
        assert reader.doc_count() == 0

    index1.add(tag="foo", content="my content")
    with index1._index.reader() as reader:
        assert reader.doc_count() == 1

    index2 = Index(app_dir=appd, index_dir=indexd)
    with index2._index.reader() as reader:
        assert reader.doc_count() == 1


def test_index_open_nonexistent_noclear(tmp_app_index_dir_paths):
    _, appd, indexd = tmp_app_index_dir_paths
    index = Index(app_dir=appd, index_dir=indexd)
    assert not exists(indexd)
    index.open(clear=False)
    assert exists(indexd)


def test_index_open_nonexistent_clear(tmp_app_index_dir_paths):
    _, appd, indexd = tmp_app_index_dir_paths
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


def test_index_search_repr(index_one):
    search = index_one.search("myquery")
    assert repr(search) == '<Search (query="text:myquery")>'


def test_index_search_tag(index_one):
    with index_one.search("tag:mytag0") as results:
        assert len(results) == 1
        assert results[0].get("content") == "mycontent0"


def test_index_search_content(index_one):
    with index_one.search("content:mycontent0") as results:
        assert len(results) == 1
        assert results[0].get("tag") == ["mytag0"]


def test_index_search_boolean(index_one):
    with index_one.search("content:mycontent0 AND tag:mytag0") as results:
        assert len(results) == 1
        assert results[0].get("tag") == ["mytag0"]


def test_results_iter(index_one):
    seen = []
    with index_one.search("tag:mytag0") as results:
        for elem in results:
            seen.append(elem)
    assert len(seen) == 1


def test_results_bool():
    _results = []
    search = object()
    results = Results(_results, search)
    assert not bool(results)
    _results.append({})
    assert bool(results)


def test_results_repr(index_one):
    search = '<Search (query="tag:mytag0")>'
    expected = "<Results (count=1, search=%s)>" % (search,)
    with index_one.search("tag:mytag0") as results:
        assert repr(results) == expected


def test_result_length(index_one):
    with index_one.search("tag:mytag0") as results:
        result = results[0]
        assert len(result) == len(result.fields.keys())


def test_result_iter(index_one):
    with index_one.search("tag:mytag0") as results:
        result = results[0]
        for key in result:
            assert key in ("tag", "id", "content", "updated")


def test_result_getitem(index_one):
    with index_one.search("tag:mytag0") as results:
        result = results[0]
        assert result["id"] == result.fields["id"]


def test_result_contains(index_one):
    with index_one.search("tag:mytag0") as results:
        result = results[0]
        assert "id" in result
        assert "foo" not in result


def test_result_repr(index_one):
    with index_one.search("tag:mytag0") as results:
        result = results[0]
        assert repr(result) == "<Result (%s)>" % (result.fields,)


def test_result_format(index_one):
    with index_one.search("tag:mytag0") as results:
        result = results[0]
        assert format(result, "{id}") == result.fields["id"]
        assert format(result, "{tags}") == ",".join(result.fields["tag"])
        assert format(result, "{content}") == result.fields["content"]


def test_index_add(index_one):
    assert len(index_one) == 1
    with index_one.search("tag:mytag1") as results:
        assert len(results) == 0
    index_one.add(**tests.test_doc1)
    assert len(index_one) == 2
    with index_one.search("tag:mytag1") as results:
        assert len(results) == 1


def test_index_add_all(index_one):
    with index_one._index.reader() as reader:
        assert reader.doc_count() == 1

    with index_one.search("tag:test_index_add_all") as results:
        assert len(results) == 0

    doc1 = {"tag": "test_index_add_all", "content": "content1"}
    doc2 = {"tag": "test_index_add_all", "content": "content2"}
    index_one.add_all([doc1, doc2])

    with index_one._index.reader() as reader:
        assert reader.doc_count() == 3

    with index_one.search("tag:test_index_add_all") as results:
        assert len(results) == 2


def test_index_remove_none(index_one):
    with index_one._index.reader() as reader:
        assert reader.doc_count() == 1
    index_one.remove()
    with index_one._index.reader() as reader:
        assert reader.doc_count() == 1


def test_index_remove_found(index_one):
    with index_one._index.reader() as reader:
        assert reader.doc_count() == 1
    docs = list(index_one)
    assert len(docs) == 1
    doc = docs[0]
    result = index_one.remove(doc["id"])
    assert result == 1
    with index_one._index.reader() as reader:
        assert reader.doc_count() == 0


def test_index_remove_not_found(index_one):
    with index_one._index.reader() as reader:
        assert reader.doc_count() == 1
    assert index_one.remove("invalidid") == 0
    with index_one._index.reader() as reader:
        assert reader.doc_count() == 1


def test_index_remove_bytes_key(index_one):
    doc = list(index_one)[0]
    assert index_one.remove(doc["id"].encode("ascii")) == 1
    with index_one._index.reader() as reader:
        assert reader.doc_count() == 0


def test_index_dump_empty(tmpd, index_empty):
    path = join(tmpd, "dump.json")
    with open(path, "w") as f:
        index_empty.dump(f)
    with open(path) as f:
        docs = json.load(f)
    assert len(docs) == 0


def test_index_dump_one(tmpd, index_one):
    path = join(tmpd, "dump.json")
    with open(path, "w") as f:
        index_one.dump(f)
    with open(path) as f:
        docs = json.load(f)
    assert len(docs) == 1
    doc = docs[0]
    assert doc["tag"] == ["mytag0"]
    assert doc["content"] == "mycontent0"


def test_index_load(tmpd, index_empty):
    path = join(tmpd, "load.json")
    with open(path, "w") as f:
        json.dump([tests.test_doc_dumped], f)
    assert len(index_empty) == 0
    with open(path, "r") as f:
        index_empty.load(f)
    assert len(index_empty) == 1
    with index_empty.search("tag:mytag") as results:
        assert len(results) == 1
        assert results[0].get("content") == tests.test_doc_dumped["content"]


def test_index_get_tags(index_one):
    tags = index_one.get_tags()
    assert tags == ["mytag0"]


def test_index_get_tags_prefix(index_one):
    assert index_one.get_tags(prefix=None) == ["mytag0"]
    assert index_one.get_tags(prefix="") == ["mytag0"]
    assert index_one.get_tags(prefix="m") == ["mytag0"]
    assert index_one.get_tags(prefix="mytag0") == ["mytag0"]
    assert index_one.get_tags(prefix="ytag") == []


def test_index_get_tags_with_counts(index_one):
    docs = [
        {"tag": "mytag2", "content": "doc1"},
        {"tag": "mytag1", "content": "doc2"},
        {"tag": "mytag0", "content": "doc3"},
        {"tag": "mytag4", "content": "doc4"},
        {"tag": "mytag3", "content": "doc5"},
        {"tag": "testtag0", "content": "doc6"},
    ]
    index_one.add_all(docs)
    expected = [
        (2, "mytag0"),
        (1, "mytag1"),
        (1, "mytag2"),
        (1, "mytag3"),
        (1, "mytag4"),
        (1, "testtag0"),
    ]
    assert index_one.get_tags(counts=True) == expected

    expected.pop()
    assert index_one.get_tags(prefix="mytag", counts=True) == expected


def test_index_pprint_default(capsys, index_one):
    index_one.pprint()
    docid = list(index_one)[0]["id"]
    expected = "id: " + util.decode(docid) + "\n"
    out, err = capsys.readouterr()
    assert not err
    assert out.startswith(expected)


def test_index_clear(index_one):
    with index_one._index.reader() as reader:
        assert reader.doc_count() == 1
    index_one.clear()
    with index_one._index.reader() as reader:
        assert reader.doc_count() == 0


def test_index_last_modified_utc(index_one):
    dt = datetime.datetime.utcfromtimestamp(index_one._index.last_modified())
    assert index_one.last_modified() == dt

    dt = index_one.last_modified(localize=True)
    now = datetime.datetime.now()
    delta = now - dt
    assert 0 < delta.total_seconds() < 1


def test_index_upgrade_not_changed(index_one):
    assert index_one.upgrade() == 0


def test_index_upgrade_changed(index_empty):
    index = index_empty
    tag = "mytag"
    content = "mycontent"
    old_id = hashlib.md5(content.encode("ascii")).hexdigest()
    new_id = schema.identifier({"content": content, "tag": tag})

    index.add(id=old_id, content=content, tag=[tag])
    with index.search("id:" + old_id) as results:
        assert len(results) == 1
        assert results[0]["id"] == old_id

    with index.search(tag) as results:
        assert len(results) == 1
        assert results[0]["id"] == old_id

    assert index.upgrade() == 1
    with index.search("id:" + old_id) as results:
        assert not results

    with index.search("id:" + new_id) as results:
        assert len(results) == 1
        assert results[0]["id"] == new_id

    assert len(index) == 1

    with index.search(tag) as results:
        assert len(results) == 1
        assert results[0]["id"] == new_id


def test_index_load_python2(monkeypatch):
    """
    Test loading a python2-generated whoosh index under python3.

    This test passes only because of the monkeypatching of
    whoosh.compat.loads with knowhow.util.pickle_loads.
    """
    expected = {
        "id": ("02a7cefe1189668fa85b56b52ee1e769" "1ee1821913f2031c8117263c07526468"),
        "content": "Hello, from Python2",
        "tag": ["python2"],
        "updated": datetime.datetime(2017, 9, 15, 14, 58, 12, 441405, tzinfo=UTC),
    }
    import knowhow

    home_dir = join(abspath(dirname(dirname(knowhow.__file__))), "data", "homepy2")
    data_dir = join(home_dir, "datapy2")

    monkeypatch.setenv("KNOWHOW_HOME", home_dir)
    monkeypatch.setenv("KNOWHOW_DATA", data_dir)

    def load_py2(data, *args, **kwargs):
        try:
            return pickle.loads(data, *args, **kwargs)
        except UnicodeDecodeError as e:
            if PYTHON2 or not e.args[0] == "ascii":
                raise

        result = pickle.loads(data, encoding="bytes")
        # need to handle a py2-pickled dict having bytes keys, which will
        # be skipped in python3, so we convert all keys to str if needed
        if isinstance(result, dict):
            d = {}
            method = result.iteritems if PYTHON2 else result.items
            for k, v in method():
                if isinstance(k, bytes):
                    k = k.decode("ascii")
                d[k] = v
            if d:
                result = d
        return result

    index = Index()
    assert len(index) == 1
    with index.search("tag:python2") as results:
        assert len(results) == 1
        with patch("whoosh.columns.loads", load_py2):
            result = results[0]
        assert sorted(result.fields.keys()) == sorted(expected.keys())
        assert result.fields == expected
