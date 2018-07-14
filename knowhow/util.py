# coding=utf8

"""
Misc utilities.
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from datetime import datetime
import sys

import pytz
import pytz.reference

import six


ISO_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f+00:00"
PYTHON2 = sys.version_info < (3,)


def decode(obj):
    """
    Decode obj to unicode if it is a byte string, trying first utf8 and then
    iso-8859-1, raising a `UnicodeDecodeError` if unable to decode a byte
    string, or returning obj unchanged if it is not a byte string.
    """
    if isinstance(obj, six.binary_type):
        try:
            obj = obj.decode("utf8")
        except UnicodeDecodeError:
            obj = obj.decode("iso-8859-1")
    return obj


def encode(obj, ascii=False):
    """
    Encode the object arg as ascii (unicode-escaped) if `ascii` true or utf8.
    """
    if isinstance(obj, six.text_type):
        obj = obj.encode("unicode-escape" if ascii else "utf8")
    return obj


def needs_ascii(fh):
    """
    Answer whether to encode as ascii for the given file handle, which is based
    on whether the handle has an encoding (None under py2 and UTF-8 under py3)
    and whether the handle is associated with a tty.
    """
    if fh.encoding and fh.encoding != "UTF-8":
        return True
    return not fh.isatty()


def json_serializer(val):
    """A JSON `default` helper function for serializing datetimes."""
    return val.isoformat() if isinstance(val, datetime) else val


def parse_datetime(val):
    """
    Parse datetime string in `ISO_DATE_FORMAT` and return a datetime value.
    """
    return datetime.strptime(val, ISO_DATE_FORMAT).replace(tzinfo=pytz.utc)


def utc_to_local(dt):
    """
    Convert UTC `datetime.datetime` instance to localtime.

    Returns a datetime with `tzinfo` set to the current local timezone.
    """
    local_timezone = pytz.reference.LocalTimezone()
    dt = dt + local_timezone.utcoffset(datetime.now())
    return dt.replace(tzinfo=local_timezone)


def strip(val):
    """
    Strip val, which may be str or iterable of str.

    For str input, returns stripped string, and for iterable input,
    returns list of str values without empty str (after strip) values.
    """
    if isinstance(val, six.string_types):
        return val.strip()
    try:
        return list(filter(None, map(strip, val)))
    except TypeError:
        return val


if PYTHON2:

    def pickle_loads(data, *args, **kwargs):
        """
        Pickle.loads replacement that handles Python2/3 gotchas.
        """
        try:
            from cPickle import loads
        except ImportError:
            from pickle import loads
        return loads(data, *args, **kwargs)


else:

    def pickle_loads(data, *args, **kwargs):
        """
        Pickle.loads replacement that handles Python2/3 gotchas.
        """
        from pickle import loads

        try:
            return loads(data, *args, **kwargs)
        except UnicodeDecodeError as e:
            print(e.args)
            if PYTHON2 or not e.args[0] == "ascii":
                raise

        result = loads(data, encoding="bytes")
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


def monkeypatch():
    """
    Monkeypatch the whoosh.compat.loads to ...
    """
    import whoosh.compat

    whoosh.compat.loads = pickle_loads
