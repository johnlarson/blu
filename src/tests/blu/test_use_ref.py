def test_ref_object_is_same_object_on_every_render():
    """Ref object is the same object from one render to the next."""
    ...


def test_init_value():
    """
    On first render, the ref's value is the value passed into use_ref.
    """
    ...


def test_value_doesnt_change_between_renders():
    """The ref's value doesn't change from one render to the next."""
    ...


def test_value_change_persists():
    """
    If the ref's value is changed, this change persists between renders.
    """
    ...


def test_setting_value_doesnt_trigger_rerender():
    """Setting a ref's value doesn't cause the element to re-render."""
    ...