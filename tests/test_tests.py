"""
Sanity checks that test helpers are actually doing what they should be doing.
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import os

from tests import env


def test_env_remove():
    try:
        os.environ['FOO'] = 'BAR'
        with env(FOO=None):
            assert 'FOO' not in os.environ
        assert os.environ['FOO'] == 'BAR'
    finally:
        os.environ.pop('FOO', None)


def test_env_add():
    assert 'FOO' not in os.environ
    with env(FOO='BAR'):
        assert os.environ['FOO'] == 'BAR'
    assert 'FOO' not in os.environ


def test_env_update():
    try:
        os.environ['FOO'] = 'BAR'
        with env(FOO='BARBAR'):
            assert os.environ['FOO'] == 'BARBAR'
        assert os.environ['FOO'] == 'BAR'
    finally:
        os.environ.pop('FOO', None)


def test_index_empty(index_empty):
    assert len(index_empty) == 0


def test_index_one(index_one):
    assert len(index_one) == 1
