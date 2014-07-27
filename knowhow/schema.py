#-*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import hashlib

import whoosh.fields as F


SCHEMA = F.Schema(

    # unique identifier
    id=F.ID(unique=True, stored=True),

    # a multi-valued analyzed field
    tag=F.TEXT(stored=True),

    # the text content of the snippet
    content=F.TEXT(stored=True),

    # when the snippet was last modified
    updated=F.DATETIME(stored=True)
)


def identifier(doc):
    """
    Generate a unique identifier based solely on the content of the document.

    This doesn't take tags or anything else into account, because the content
    is what really matters. This means that adding the same content with
    different tags is equivalent to just updating the tags of the existing
    document, which is the desired behavior.
    """
    data = doc.get('content').encode('utf-8')
    return hashlib.md5(data).hexdigest()
