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

import six

from six.moves.configparser import NoSectionError, NoOptionError
try:
    from six.moves.configparser import SafeConfigParser as ConfigParser
except ImportError:  # py3
    from.six.moves.configparser import ConfigParser


iso_date_format = '%Y-%m-%dT%H:%M:%S.%f+00:00'


def decode(obj):
    """
    Decode obj to unicode if it is a byte string, trying first utf8 and then
    iso-8859-1, raising a `UnicodeDecodeError` if unable to decode a byte
    string, or returning obj unchanged if it is not a byte string.
    """
    if isinstance(obj, six.binary_type):
        try:
            obj = obj.decode('utf8')
        except UnicodeDecodeError:
            obj = obj.decode('iso-8859-1')
    return obj


def encode(obj, ascii=False):
    if isinstance(obj, six.text_type):
        obj = obj.encode('unicode-escape' if ascii else 'utf8')
    return obj


def is_ascii_console():
    return sys.stdout.encoding != 'UTF-8'


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
