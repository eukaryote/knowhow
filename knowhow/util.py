def strip(val):
    """
    Recursively strip whitespace from strings and arbitrarily nested
    strings in dicts or iterable containers, preserving all container types
    (e.g., tuples remain tuples in output, lists remain list in output,
    etc.). Any non-standard (non-dict) iterable types must have an
    `__init__` that accepts a list as the first parameter for creation
    of a new instance, just as `list` and `tuple` themselves do.
    """
    # Not very efficient, but it's nice to be able to preserve types;
    # of course, not needed above at all, since the values above
    # can only be lists that are not nested.
    if isinstance(val, str):
        return val.strip()
    elif isinstance(val, dict):
        return type(val)({k: strip(val[k]) for k in val})
    try:
        return type(val)(map(strip, val))
    except TypeError:  # not iterable
        return val     # everything else returned as is
