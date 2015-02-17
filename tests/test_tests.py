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
