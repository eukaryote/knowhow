# coding=utf8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import os
from os.path import exists
import sys
import pytz
import pytz.reference
from datetime import datetime

try:
    from configparser import NoSectionError, NoOptionError, ConfigParser
except ImportError:  # py2
    from ConfigParser import (NoSectionError, NoOptionError,
                              SafeConfigParser as ConfigParser)


iso_date_format = '%Y-%m-%dT%H:%M:%S.%f+00:00'


def json_serializer(val):
    return val.isoformat() if isinstance(val, datetime) else val


def parse_datetime(val):
    if not val:
        return val
    d = datetime.strptime(val, iso_date_format)
    d = d.replace(tzinfo=pytz.utc)
    return d


def utc_to_local(dt):
    """
    Convert UTC `datetime.datetime` instance to localtime.

    Returns a datetime with `tzinfo` set to the current local timezone.
    """
    local_timezone = pytz.reference.LocalTimezone()
    dt = dt + local_timezone.utcoffset(datetime.now())
    return dt.replace(tzinfo=local_timezone)


def get_app_dir(platform=None):
    path = os.environ.get('KNOWHOW_HOME')
    if path:
        return path
    elif (platform or sys.platform) == 'win32':
        return os.path.join(os.environ['APPDATA'], 'knowhow')
    else:  # *nix...
        return os.path.join(os.environ['HOME'], '.knowhow')


def get_config(app_dir=None, platform=None):
    conf = ConfigParser()
    path = os.environ.get('KNOWHOW_CONF')
    if not path:
        if not app_dir:
            app_dir = get_app_dir(platform=platform)
        assert app_dir
        path = os.path.join(app_dir, 'knowhow.ini')
    if exists(path):
        conf.read(path)
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
