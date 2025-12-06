def test_args():
    """
    Calling a ClientElement as a function returns a copy that will be
    rendered by passing in the positional args the original was called
    with into its render function.
    """
    ...


def test_kwargs():
    """
    Calling a ClientElement as a function returns a copy that will be
    rendered by passing in the keyword args the original was called with
    into its render function.
    """
    ...


def test_args_and_kwargs():
    """
    Calling a ClientElement as a function returns a copy that will be
    rendered by passing in both the positional and keyword args the
    original was called with into its render function.
    """
    ...


def test_replace_original_args_and_kwargs():
    """
    When a ClientElement is called as a function to create a copy, none
    of the original positional or keyword arguments will be retained in
    the copy.
    """
    ...


def test_key():
    """
    Passing the keyword argument "key" into a ClientElement's __call__
    method results in ClientElement that has the provided key.
    """
    ...


def test_key_not_passed_into_render_function():
    """
    Passing the keyword argument "key" into a ClientElement's __call__
    method doesn't result in the "key" keyword argument being passed on
    to the render function during rendering.
    """
    ...


def test_call_replaces_key():
    """
    If a "key" keyword argument is specified in ClientElement.__call__,
    that will be the key of the resulting copy, regardless of what the
    original key was.
    """
    ...


def test_call_does_not_retain_key():
    """
    If no key is specified in a call to ClientElement.__call__, the
    resulting copy will not have a key, even if the original did.
    """
    ...


def test_call_retains_children():
    """
    When a ClientElement is called as a function, the resulting copy has
    the same children as the original.
    """
    ...


def test_call_does_not_mutate_original():
    """
    Calling a ClientElement as a function does not mutate the original
    in place.
    """
    ...


def test_children():
    """
    __getitem__ returns a copy that will be rendered as the original,
    but with the items passed into __getitem__ being rendered where the
    yield statement appears.
    """
    ...


def test_no_children():
    """
    Rendering an element that never had children added using __getitem__
    will result in nothing being rendered where the yield statement is.
    """
    ...


def test_doesnt_take_children():
    """
    When a ClientElement doesn't accept children, i.e. its rendering
    function has no yield statement, calling __getitem__ raises a
    TypeError.
    """
    ...


def test_replace_children():
    """
    When ClientElement.__getitem__ is called, the resulting copy does
    not retain the original's children.
    """
    ...


def test_getitem_retains_original_args_and_kwargs():
    """
    When ClientElement.__getitem__ is called, the resulting copy has the
    same positional and keyword render arguments as the original.
    """
    ...


def test_getitem_retains_key():
    """
    When ClientElement.__getitem__ is called, the resulting copy has the
    same key as the original.
    """
    ...


def test_getitem_does_not_mutate_original():
    """
    ClientElement.__getitem__ does not mutate the original in place.
    """
    ...


def test_renders_correctly():
    """
    ClientElements render as expected client-side.

    This test checks core functionality in a client-side environment to
    ensure the functionality seen in the other tests in this module
    translate to the expected behavior in an actual Blu app.

    Most tests don't run in a full app environment because it would be
    very slow to test all functionality in a web browser.
    """
    ...
