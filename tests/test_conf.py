# coding=utf8
# pylint: disable=missing-docstring,invalid-name

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import os

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from knowhow import conf

from tests import env


def test_get_app_dir_env_set():
    path = '/app'
    with env(KNOWHOW_HOME=path):
        assert conf.get_app_dir() == path


def test_get_app_dir_windows():
    appdata = r'C:\\Users\\Foo\\AppData\\Roaming'
    expected = os.path.join(appdata, 'knowhow')
    with env(APPDATA=appdata):
        assert conf.get_app_dir(platform='win32') == expected


def test_get_app_dir_other():
    for platform in ['linux', 'cygwin', 'darwin']:
        home = '/home/foo'
        expected = os.path.join(home, '.knowhow')
        with env(HOME=home):
            assert conf.get_app_dir(platform=platform) == expected


def test_get_config_no_env():
    app_dir = '/tmp/test_get_config'
    assert 'KNOWHOW_CONF' not in os.environ
    with patch('knowhow.conf.get_app_dir', return_value=app_dir) as mock:
        assert conf.get_config()
    mock.assert_called_once_with(platform=None)


def test_get_config_using_env(conf_path):
    with env(KNOWHOW_CONF=conf_path):
        c = conf.get_config()
        assert c.get('main', 'data') == '/app/data'


def test_get_data_dir_env_set():
    path = '/data'
    with env(KNOWHOW_DATA=path):
        assert conf.get_data_dir() == path


def test_get_data_dir_env_unset(conf_path):
    conf_dir = os.path.dirname(conf_path)
    with env(KNOWHOW_DATA=None, KNOWHOW_HOME=conf_dir):
        assert conf.get_data_dir() == '/app/data'
        assert conf.get_data_dir(app_dir=conf_dir) == '/app/data'


def test_get_data_dir_custom(conf_path):
    assert 'KNOWHOW_DATA' not in os.environ

    app_dir = os.path.dirname(conf_path)
    data_dir = os.path.join(app_dir, 'test_get_data_dir_custom')

    # create a conf file with an option in 'main' but no 'data' option
    with open(conf_path, 'wb') as fh:
        fh.write(b'[main]\n')
        fh.write(b'data = ')
        fh.write(data_dir.encode('ascii'))
        fh.write(b'\n')

    assert conf.get_data_dir(app_dir=app_dir) == data_dir


def test_get_data_dir_default(conf_path):
    assert 'KNOWHOW_DATA' not in os.environ

    app_dir = os.path.dirname(conf_path)

    # create a conf file with an option in 'main' but no 'data' option
    with open(conf_path, 'wb') as fh:
        fh.write(b'[main]\n')
        fh.write(b'foo = bar\n')

    config = conf.get_config(app_dir=app_dir)

    # verify file is valid and we can read the option we added to main
    assert config.get('main', 'foo') == 'bar'

    # verify that reading data option handles error and uses default
    data_dir = conf.get_data_dir(app_dir=app_dir)

    assert data_dir == os.path.join(app_dir, 'data')
