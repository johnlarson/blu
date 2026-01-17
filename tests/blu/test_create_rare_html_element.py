from blu import HTMLElement, create_rare_html_element


def test_create_element():
    """
    Returns an HTMLElement whose tag name exactly matches the provided
    tag name.
    """
    element = create_rare_html_element('my_element-_')
    assert isinstance(element, HTMLElement)
    assert element._tagname == 'my_element-_'  # type: ignore


def test_no_props():
    """The HTMLElement returned has no props."""
    assert create_rare_html_element('a')._attrs == {}  # type: ignore


def test_no_children():
    """The HTMLElement returned has no children."""
    assert create_rare_html_element('a')._children == []  # type: ignore