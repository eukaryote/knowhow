# coding=utf8
# pylint: disable=missing-docstring,invalid-name

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import sys
from datetime import datetime

import pytz

import pytest

import six
try:
    import unittest.mock as mock
except ImportError:
    import mock

import knowhow.util as util


def test_decode_nonstr():
    assert util.decode(0) == 0


def test_decode_ascii():
    bs = 'asdf'.encode('ascii')
    assert isinstance(bs, six.binary_type)
    s = util.decode(bs)
    assert isinstance(s, six.text_type)
    assert s == 'asdf'


def test_decode_utf8():
    bs = 'चतरस'.encode('utf8')
    assert isinstance(bs, six.binary_type)
    s = util.decode(bs)
    assert isinstance(s, six.text_type)
    assert s == 'चतरस'


def test_decode_iso88591():
    bs = 'café'.encode('iso-8859-1')
    with pytest.raises(UnicodeDecodeError):
        bs.decode('utf8')
    assert util.decode(bs) == 'café'


def test_encode_nonstr():
    assert util.encode(0) == 0


def test_encode_ascii():
    assert util.encode('café', True) == six.b(r'caf\xe9')


def test_encode_utf8():
    assert util.encode('café', False) == 'café'.encode('utf8')


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
    nownaive = datetime.now()
    nowlocal = util.utc_to_local(datetime.utcnow())
    epochnaive = int(nownaive.strftime('%s'))
    epochlocal = int(nowlocal.strftime('%s'))
    assert abs(epochnaive - epochlocal) < 1


def test_needs_ascii_no_encoding_tty():
    with mock.patch('tests.test_util.sys.stdout') as fh:
        fh.encoding = None
        fh.isatty.return_value = True
        assert not util.needs_ascii(sys.stdout)


def test_needs_ascii_no_encoding_no_tty():
    with mock.patch('tests.test_util.sys.stdout') as fh:
        fh.encoding = None
        fh.isatty.return_value = False
        assert util.needs_ascii(fh)


def test_needs_ascii_encoding_utf8_tty():
    with mock.patch('tests.test_util.sys.stdout') as fh:
        fh.encoding = 'UTF-8'
        fh.isatty.return_value = True
        assert not util.needs_ascii(fh)


def test_needs_ascii_encoding_utf8_no_tty():
    with mock.patch('tests.test_util.sys.stdout') as fh:
        fh.encoding = 'UTF-8'
        fh.isatty.return_value = False
        assert util.needs_ascii(fh)


def test_needs_ascii_encoding_ascii_tty():
    with mock.patch('tests.test_util.sys.stdout') as fh:
        fh.encoding = 'ascii'
        fh.isatty.return_value = True
        assert util.needs_ascii(fh)


def test_needs_ascii_encoding_ascii_no_tty():
    with mock.patch('tests.test_util.sys.stdout') as fh:
        fh.encoding = 'ascii'
        fh.isatty.return_value = False
        assert util.needs_ascii(fh)
