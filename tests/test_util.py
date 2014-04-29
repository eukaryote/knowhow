from knowhow.util import strip

class mylist(list):
    pass


def test_strip_none():
    assert strip(None) is None


def test_strip_empty_string():
    assert strip('') == ''


def test_strip_int():
    assert strip(4) == 4


def test_strip_empties():
    for val in [(), [], mylist()]:
        val_type_orig = type(val)
        new_val = strip(val)
        assert new_val == val
        assert type(new_val) == val_type_orig


def test_strip_lists():
    assert strip([1, ' ']) == [1, '']
