from blu import Ref


def test_set_and_get():
    """
    Once a ref's value is set using __setitem__, that value will be
    returned by __getitem__.
    """
    ref: Ref[int] = Ref()
    ref[:] = 1
    assert ref[:] == 1



def test_change_value():
    """A ref's value can be changed after it's set the first time."""
    ref: Ref[int] = Ref()
    ref[:] = 1
    ref[:] = 2
    assert ref[:] == 2
