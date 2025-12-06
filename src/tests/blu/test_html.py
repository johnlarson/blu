def test_element_has_imported_tagname():
    """
    The imported element's tag name is the same as the name it was
    imported as.
    """
    ...


def test_element_has_no_props():
    """The imported element has no props."""
    ...


def test_element_has_no_children():
    """The imported element has no children."""
    ...


def test_trailing_underscore():
    """
    An imported element with a trailing underscore in its imported name
    should not include the trailing underscore in its tag name.
    """
    ...


def test_non_trailing_underscore():
    """
    Non-trailing underscores in the import name should appear in the tag
    name as dashes.
    """
    ...


def test_multiple_trailing_underscores():
    """
    If the import name has multiple trailing underscores, only the last
    one is removed from the tag name; the others show up as dashes.
    """
    ...