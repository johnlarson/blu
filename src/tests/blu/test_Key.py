def test_uses_key():
    """The key passed in is used."""
    ...


def renders_children():
    """Renders as its children."""
    ...


def test_no_children():
    """
    Rendering a Key that never had children added using __getitem__ will
    result in nothing being rendered where the Key appears.
    """
    ...


def test_replace_children():
    """
    When Key.__getitem__ is called, the resulting copy does not retain
    the original's children.
    """
    ...


def test_getitem_retains_key():
    """
    When Key.__getitem__ is called, the resulting copy has the same key
    as the original.
    """
    ...


def test_getitem_does_not_mutate_original():
    """Key.__getitem__ does not mutate the original in place."""
    ...


def test_accepts_any_node_children():
    """Accepts any blu.Node as a child."""
    ...


def test_accepts_children_with_children():
    """Renders correctly with element children that have children."""
    ...


def test_renders_correctly():
    """
    Keys render as expected client-side.

    This test checks core functionality in a client-side environment to
    ensure the functionality seen in the other tests in this module
    translate to the expected behavior in an actual Blu app.

    Most tests don't run in a full app environment because it would be
    very slow to test all functionality in a web browser.
    """
    ...