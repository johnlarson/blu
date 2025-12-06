def test_uses_key():
    """The key passed in is used."""
    ...


def renders_children():
    """Renders as its children."""
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