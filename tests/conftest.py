from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import os
from os.path import join
import tempfile
import shutil

from six.moves import configparser

import pytest

from tests import setenv, test_doc0

from knowhow.index import Index
import knowhow.util as util


@pytest.fixture
def tmpd(request):
    tempdir = tempfile.mkdtemp()
    request.addfinalizer(lambda: shutil.rmtree(tempdir))
    return tempdir


@pytest.fixture
def conf():
    try:
        conf = configparser.SafeConfigParser()
    except AttributeError:
        conf = configparser.ConfigParser()
    conf.add_section('main')
    conf.set('main', 'data', util.decode('/app/data'))
    return conf


@pytest.fixture
def conf_path(conf, tmpd):
    print('conf: %s' % conf)
    path = join(tmpd, 'knowhow.ini')
    with open(path, 'w') as f:
        conf.write(f)
    return path


@pytest.fixture
def tmp_app_index_dir_paths(tmpd):
    app_dir = join(tmpd, 'app')
    index_dir = join(tmpd, 'index')
    return tmpd, app_dir, index_dir


@pytest.fixture
def tmp_app_index_dirs(tmp_app_index_dir_paths):
    tmpd, appd, indexd = tmp_app_index_dir_paths
    os.mkdir(appd)
    os.mkdir(indexd)
    return tmpd, appd, indexd


@pytest.fixture
def index_empty(request, tmp_app_index_dirs):
    tmpd, app_dir, index_dir = tmp_app_index_dirs

    orig_home = os.environ.get('KNOWHOW_HOME')
    orig_data = os.environ.get('KNOWHOW_DATA')

    def restore():
        setenv('KNOWHOW_HOME', orig_home)
        setenv('KNOWHOW_DATA', orig_data)

    request.addfinalizer(restore)

    os.environ['KNOWHOW_HOME'] = app_dir
    os.environ['KNOWHOW_DATA'] = index_dir
    index = Index(app_dir=app_dir, index_dir=index_dir)
    index.open(clear=True)
    return index


@pytest.fixture
def index_one(index_empty):
    index_empty.add(**test_doc0)
    return index_empty
