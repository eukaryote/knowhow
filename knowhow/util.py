from __future__ import print_function

import os
import sys
try:
    from configparser import NoSectionError, NoOptionError, ConfigParser
except ImportError:  # py2
    from ConfigParser import (NoSectionError, NoOptionError,
                              SafeConfigParser as ConfigParser)

from datetime import datetime
import pytz


iso_date_format = '%Y-%m-%dT%H:%M:%S.%f+00:00'


def json_serializer(val):
    return val.isoformat() if isinstance(val, datetime) else val


def parse_datetime(val):
    if not val:
        return val
    d = datetime.strptime(val, iso_date_format)
    d = d.replace(tzinfo=pytz.utc)
    return d


def get_app_dir(platform=None):
    path = os.environ.get('KNOWHOW_HOME')
    if path:
        return path
    elif (platform or sys.platform).lower() in ['win32', 'win64']:
        return os.path.join(os.environ['APPDATA'], 'knowhow')
    else:  # *nix...
        return os.path.join(os.environ['HOME'], '.knowhow')


def get_config(app_dir=None, platform=None):
    path = os.environ.get('KNOWHOW_CONF')
    if path:
        if not os.path.exists(path):
            raise Exception('KNOWHOW_CONF file does not exist: ' + path)
    else:
        if not app_dir:
            app_dir = get_app_dir(platform=platform)
        assert app_dir
        path = os.path.join(app_dir, 'knowhow.ini')
    conf = ConfigParser()
    try:
        with open(path, 'r') as f:
            conf.read_file(f)
    except IOError:
        pass  # use new empty conf
    return conf


def get_data_dir(app_dir=None, platform=None):
    path = os.environ.get('KNOWHOW_DATA')
    if path:
        return path
    # if no env var given, then try to load from config file
    if not app_dir:
        app_dir = get_app_dir(platform=platform)
    config = get_config(app_dir=app_dir)
    try:
        path = config.get('main', 'data')  # no fallback kwarg in py2
    except (NoSectionError, NoOptionError):
        path = None
    return path if path else os.path.join(app_dir, 'data')
