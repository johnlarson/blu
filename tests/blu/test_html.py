from blu import HTMLElement


def test_element_is_instance_of_HTMLElement():
    """Anything imported from blu.html should be an HTMLElement."""
    from blu.html import element
    assert isinstance(element, HTMLElement)


def test_element_has_imported_tagname():
    """
    The imported element's tag name is the same as the name it was
    imported as.
    """
    from blu.html import blah
    assert blah._tagname == 'blah'  # type: ignore


def test_element_has_no_props():
    """The imported element has no props."""
    from blu.html import element
    assert element._attrs == {}  # type: ignore


def test_element_has_no_children():
    """The imported element has no children."""
    from blu.html import element
    assert element._children == []  # type: ignore


def test_trailing_underscore():
    """
    An imported element with a trailing underscore in its imported name
    should not include the trailing underscore in its tag name.
    """
    from blu.html import del_
    assert del_._tagname == 'del'  # type: ignore


def test_non_trailing_underscore():
    """
    Non-trailing underscores in the import name should appear in the tag
    name as dashes.
    """
    from blu.html import _my_element
    assert _my_element._tagname == '-my-element'  # type: ignore


def test_multiple_trailing_underscores():
    """
    If the import name has multiple trailing underscores, only the last
    one is removed from the tag name; the others show up as dashes.
    """
    from blu.html import blah__
    assert blah__._tagname == 'blah-'  # type: ignore