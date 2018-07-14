# coding=utf8

"""
Schema for an item of "know how".

A knowhow item has an id, optional tags, text content, and a modification date.
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import hashlib

import whoosh.fields as F

# This scheme defines the structure of a single knowhow snippet.
SCHEMA = F.Schema(
    # unique identifier
    id=F.ID(unique=True, stored=True),
    # a multi-valued analyzed field
    tag=F.KEYWORD(stored=True, field_boost=2.0),
    # the text content of the snippet
    content=F.TEXT(stored=True),
    # all searchable fields, for use as a default field
    text=F.TEXT(stored=False),
    # when the snippet was last modified
    updated=F.DATETIME(stored=True),
)

# Function to create a hasher object for generating id of a snippet.
IdGenerator = hashlib.sha256

# The number of hexadecimal characters in an id
ID_LENGTH = IdGenerator().digest_size * 2


def identifier(doc):
    """
    Generate a unique identifier based solely on the content of the document.

    This doesn't take tags or anything else into account, because the content
    is what really matters. This means that adding the same content with
    different tags is equivalent to just updating the tags of the existing
    document, which is the desired behavior.
    """
    data = doc.get("content").strip().encode("utf-8")
    return IdGenerator(data).hexdigest()
