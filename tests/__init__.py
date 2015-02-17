import os
from contextlib import contextmanager

import six


@contextmanager
def env(**kw):
    originals = {}
    # store original environ values to be changed and apply changes
    for k, v in six.iteritems(kw):
        original = os.environ.get(k)
        if v is not None:
            os.environ[k] = v
        elif original is not None:
            os.environ.pop(k)
        originals[k] = original
    yield
    # restore original values
    for k, v in six.iteritems(kw):
        original = originals[k]
        if original is not None:
            os.environ[k] = original
        elif v is not None:
            os.environ.pop(k)
