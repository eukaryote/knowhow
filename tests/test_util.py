from knowhow.util import strip


def test_strip_none():
    assert strip(None) is None


def test_strip_empty_string():
    assert strip('') == ''


def test_strip_int():
    assert strip(4) == 4


def test_strip_empties():

    class mylist(list):
        pass
    for val in [(), [], mylist()]:
        new_val = strip(val)
        assert new_val == val
        assert type(new_val) is type(val)


def test_strip_lists():
    assert strip([1, ' ']) == [1, '']
    assert strip(['ab  ', '  a  b  cx ']) == ['ab', 'a  b  cx']


def test_strip_mixed():
    val = (' a ',
           [3, '  b', 'd'],
           {'a  ': [1, '  b']})
    assert strip(val) == ('a', [3, 'b', 'd'], {'a  ': [1, 'b']})


def test_custom_dict():

    class mydict(dict):
        pass

    val = mydict(
        a=mydict([('b', ' c ')]),
        b=None,
        c=(1, ' x ')
    )
    val_new = strip(val)
    assert type(val_new) is type(val)
    assert val_new == mydict(a=mydict(b='c'), b=None, c=(1, 'x'))
