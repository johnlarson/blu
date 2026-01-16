def test_str_render():
    """A str renders as the text of the str."""
    ...


def test_tuple_render():
    """A tuple renders as the items in the tuple, one after another."""
    ...


def test_iterable_render():
    """
    An iterable renders as the items in the iterable, one after another.
    """
    ...


def test_int_render():
    """An int i renders as str(i)."""
    ...


def test_float_render():
    """A float f renders as str(f)"""
    ...


def test_true_render():
    """True renders as "true"."""
    ...


def test_false_render():
    """False renders as "false"."""
    ...


def test_none_render():
    """Nothing is rendered where None appears."""
    ...


def test_renders_correctly_on_client():
    """
    Nodes render as expected client-side.

    This test checks core functionality in a client-side environment to
    ensure the functionality seen in the other tests in this module
    translate to the expected behavior in an actual Blu app.

    Most tests don't run in a full app environment because it would be
    very slow to test all functionality in a web browser.
    """
    ...