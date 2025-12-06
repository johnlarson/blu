def test_intial_render():
    """
    On initial render, the state value is the value passed into
    use_state().
    """
    ...


def test_use_setter():
    """
    When the setter is used, a re-render will be triggered, and when
    the re-render happens, the value of the state will be the value
    passed into the setter.
    """
    ...


def test_external_rerender():
    """
    If the setter is never called, the initial value is used on all
    re-renders triggered by other states.
    """
    ...


def test_set_value_persists():
    """
    If the setter is used, the value passed in will persist in all
    future re-renders if it is not changed.
    """
    ...


def test_value_set_multiple_times():
    """
    The state can be set multiple times, and still persists between
    renders until the setter is called again.
    """
    ...