# coding=utf8

"""
Configuration resources.
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import os
import sys

from six.moves.configparser import NoSectionError, NoOptionError

try:
    from six.moves.configparser import SafeConfigParser as ConfigParser  # PY3
except ImportError:  # PY2
    from .six.moves.configparser import ConfigParser  # PY2

PYTHON2 = sys.version_info < (3,)


def get_app_dir(platform=None):
    """
    Get path to main application directory.
    """
    path = os.environ.get("KNOWHOW_HOME")
    if path:
        return path
    elif (platform or sys.platform) == "win32":
        return os.path.join(os.environ["APPDATA"], "knowhow")
    else:
        return os.path.join(os.environ["HOME"], ".knowhow")


def get_config(app_dir=None, platform=None):
    """
    Load app configuration and return as config instance.
    """
    config = ConfigParser()
    path = os.environ.get("KNOWHOW_CONF")
    if not path:
        if not app_dir:
            app_dir = get_app_dir(platform=platform)
        assert app_dir
        path = os.path.join(app_dir, "knowhow.ini")
    if os.path.exists(path):
        config.read(path)
    return config


def get_data_dir(app_dir=None, platform=None):
    """
    Get path to data directory that contains index.
    """
    path = os.environ.get("KNOWHOW_DATA")
    if path:
        return path
    # if no env var given, then try to load from config file
    if not app_dir:
        app_dir = get_app_dir(platform=platform)
    config = get_config(app_dir=app_dir)
    try:
        path = config.get("main", "data")  # no fallback kwarg in py2
    except (NoSectionError, NoOptionError):
        path = None
    return path if path else os.path.join(app_dir, "data")
