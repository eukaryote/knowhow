from os.path import join, dirname
from datetime import datetime
import time
import pytz

import knowhow.util as util

from tests import env


def test_get_app_dir_env_set():
    path = '/app'
    with env(KNOWHOW_HOME=path):
        assert util.get_app_dir() == path


def test_get_app_dir_windows():
    appdata = r'C:\\Users\\Foo\\AppData\\Roaming'
    expected = join(appdata, 'knowhow')
    with env(APPDATA=appdata):
        assert util.get_app_dir(platform='win32') == expected


def test_get_app_dir_other():
    for platform in ['linux', 'cygwin', 'darwin']:
        home = '/home/foo'
        expected = join(home, '.knowhow')
        with env(HOME=home):
            assert util.get_app_dir(platform=platform) == expected


def test_get_config_env_set(conf_path):
    with env(KNOWHOW_CONF=conf_path):
        conf = util.get_config()
        assert conf.get('main', 'data') == '/app/data'


def test_get_data_dir_env_set():
    path = '/data'
    with env(KNOWHOW_DATA=path):
        assert util.get_data_dir() == path


def test_get_data_dir_env_unset(conf_path):
    conf_dir = dirname(conf_path)
    with env(KNOWHOW_DATA=None, KNOWHOW_HOME=conf_dir):
        assert util.get_data_dir() == '/app/data'
        assert util.get_data_dir(app_dir=conf_dir) == '/app/data'


def test_parsedatetime_utc():
    # iso_date_format = '%Y-%m-%dT%H:%M:%S.%f+00:00'
    dt = util.parse_datetime('2014-12-31T23:59:59.000001+00:00')
    assert dt.year == 2014
    assert dt.month == 12
    assert dt.day == 31
    assert dt.hour == 23
    assert dt.minute == 59
    assert dt.second == 59
    assert dt.microsecond == 1
    assert dt.tzinfo == pytz.UTC


def test_utc_to_local():
    expected_offset = time.timezone
    nownaive = datetime.now()
    nowlocal = util.utc_to_local(datetime.utcnow())
    local_offset = nowlocal.utcoffset()
    if local_offset.days == -1:
        expected_offset = (24 * 3600) - expected_offset
    assert local_offset.seconds == expected_offset
    epochnaive = int(nownaive.strftime('%s'))
    epochlocal = int(nowlocal.strftime('%s'))
    assert abs(epochnaive - epochlocal) < 1
