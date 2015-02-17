from os.path import join
import tempfile
import shutil

from six.moves import configparser

import pytest


@pytest.fixture
def index(request):
    pass


@pytest.fixture
def tmpd(request):
    tempdir = tempfile.mkdtemp()
    request.addfinalizer(lambda: shutil.rmtree(tempdir))
    return tempdir


@pytest.fixture
def conf_path(conf, tmpd):
    path = join(tmpd, 'knowhow.ini')
    with open(path, 'wb') as f:
        conf.write(f)
    return path


@pytest.fixture
def conf():
    try:
        conf = configparser.SafeConfigParser()
    except AttributeError:
        conf = configparser.ConfigParser()
    conf.add_section('main')
    conf.set('main', 'data', '/app/data')
    return conf
