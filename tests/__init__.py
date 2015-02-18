# coding=utf8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import datetime
import os
from contextlib import contextmanager

import six

test_doc0 = {
    'tag': 'mytag0',
    'content': 'mycontent0',
    'updated': datetime.datetime.now()
}

test_doc1 = {
    'tag': 'mytag1',
    'content': 'mycontent1',
    'updated': datetime.datetime.now()
}

test_doc_dumped = {
    'content': 'mycontent',
    'tag': ['mytag'],
    'id': 'c8afdb36c52cf4727836669019e69222',
    'updated': '2014-05-04T14:20:12.824058+00:00'
}


def setenv(k, v=None):
    if v is None:
        os.environ.pop(k, None)
    else:
        os.environ[k] = v


@contextmanager
def env(**kw):
    originals = {}
    # store original environ values to be changed and apply changes
    for k, v in six.iteritems(kw):
        originals[k] = os.environ.get(k)
        setenv(k, v)
    yield
    # restore original values
    for k, v in six.iteritems(kw):
        setenv(k, originals[k])
