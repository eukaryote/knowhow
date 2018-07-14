# coding=utf8

"""
knowhow is a searchable and scriptable knowledge repository for useful snippets
of information that are worth saving for future reference. It consists of a
library for programmatic use, and a commandline script for interactive usage.
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division


__version_info__ = (0, 8, 0)
__version__ = ".".join(map(str, __version_info__))

# no imports here, because this is imported by setup.py to get the version
