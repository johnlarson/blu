def test_kwarg_props():
    """
    Keyword arguments passed into HTMLElement.__call__ are passed as
    props when the HTMLElement is rendered.
    """
    ...


def test_trailing_underscore():
    """
    When a keyword argument to HTMLElement.__call__ has a trailing
    underscore in the argument name, the trailing underscore will not
    appear in the resulting React HTML element.
    """
    ...


def test_non_trailing_underscore():
    """
    When a keyword argument to HTMLElement.__call__ has a non-trailing
    underscore in the argument name, the underscore will be converted to
    a dash in the resulting React HTML element.
    """
    ...


def test_props_dict():
    """
    When a dict is passed as the first positional argument to
    HTMLElement.__call__, its keyword-value pairs are passed as props
    to the resulting React HTML element.
    """
    ...


def test_props_dict_kwargs_conflicts():
    """
    If there is a conflict between the positional argument dict and the
    keyword arguments in HTMLElement.__call__, the positional argument
    will take precedence.
    """
    ...


def test_replace_original_props():
    """
    When HTMLElement.__call__ is called, the resulting HTMLElement will
    not include the original's props, other than children.
    """
    ...


def test_call_retains_children():
    """
    When HTMLElement.__call__ is called, the resulting HTMLElement will
    have the same children as the original.
    """
    ...


def test_call_does_not_mutate_original():
    """
    Calling HTMLElement.__call__ does not mutate the original in place.
    """
    ...


def test_children():
    """
    Calling HTMLElement.__getitem__ returns a copy whose children are
    the Nodes passed into the square brackets.
    """
    ...


def test_no_children():
    """
    An HTMLElement with no children will render as and HTML element with
    no children.
    """
    ...


def test_replace_children():
    """
    When HTMLElement.__getitem__ is called, the returned copy will not
    retain the original's children.
    """
    ...


def test_getitem_retains_original_props():
    """
    When HTMLElement.__getitem__ is called, the returned copy will have
    the same non-children props as the original.
    """
    ...


def test_getitem_does_not_mutate_original():
    """
    Calling HTMLElement.__getitem__ does not mutate the original in
    place.
    """
    ...


def test_accepts_any_node_children():
    """Accepts any blu.Node as a child."""
    ...


def test_accepts_children_with_children():
    """Renders correctly with element children that have children."""
    ...


def test_renders_correctly():
    """
    HTMLElements render as expected client-side.

    This test checks core functionality in a client-side environment to
    ensure the functionality seen in the other tests in this module
    translate to the expected behavior in an actual Blu app.

    Most tests don't run in a full app environment because it would be
    very slow to test all functionality in a web browser.
    """
    ...