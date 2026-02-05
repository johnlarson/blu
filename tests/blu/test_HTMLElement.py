from blu._nodes import Key, client
from blu.html import div, span
from tests.utils import node_eq, renders_as


def test_kwarg_props():
    """
    Keyword arguments passed into HTMLElement.__call__ are stored in the
    _attrs attribute.
    """
    assert div(id=3)._attrs["id"] == 3


def test_trailing_underscore():
    """
    When a keyword argument to HTMLElement.__call__ has a trailing
    underscore in the argument name, the trailing underscore will not
    appear in the attribute name.
    """
    assert div(id_=3)._attrs["id"] == 3


def test_non_trailing_underscore():
    """
    When a keyword argument to HTMLElement.__call__ has a non-trailing
    underscore in the argument name, the underscore will be converted to
    a dash in the attribute name.
    """
    assert div(data_count=3)._attrs["data-count"] == 3


def test_props_dict():
    """
    When a dict is passed as the first positional argument to
    HTMLElement.__call__, its keyword-value pairs are passed are set as
    attributes with the exact names as the keys in the dict.
    """
    assert div({"my_-attr_": 3})._attrs["my_-attr_"] == 3  # type: ignore


def test_props_dict_kwargs_conflicts():
    """
    If there is a conflict between the positional argument dict and the
    keyword arguments in HTMLElement.__call__, the positional argument
    will take precedence.
    """
    assert div({"id": 1}, id=2)._attrs["id"] == 2  # type: ignore


def test_replace_original_props():
    """
    When HTMLElement.__call__ is called, the resulting HTMLElement will
    not include the original's props, other than children.
    """
    assert div(id=1)(id=2)._attrs["id"] == 2  # type: ignore


def test_call_retains_children():
    """
    When HTMLElement.__call__ is called, the resulting HTMLElement will
    have the same children as the original.
    """
    assert div["Hello!"](id=1)._children == ["Hello!"]  # type: ignore


def test_call_does_not_mutate_original():
    """
    Calling HTMLElement.__call__ does not mutate the original in place.
    """
    original = div(id=1)
    original(id=2)
    assert original._attrs["id"] == 1  # type: ignore


def test_children():
    """
    Calling HTMLElement.__getitem__ returns a copy whose children are
    the Nodes passed into the square brackets.
    """
    assert div[1, 2, 3]._children == [1, 2, 3]  # type: ignore


def test_no_children():
    """
    For an HTMLElement with no children specified, the _children
    attribute is [].
    """
    assert div._children == []  # type: ignore


def test_replace_children():
    """
    When HTMLElement.__getitem__ is called, the returned copy will not
    retain the original's children.
    """
    assert div[1, 2, 3][4, 5, 6]._children == [4, 5, 6]  # type: ignore


def test_getitem_retains_original_props():
    """
    When HTMLElement.__getitem__ is called, the returned copy will have
    the same non-children props as the original.
    """
    assert div(id=1)["Hello"]._attrs["id"] == 1  # type: ignore


def test_getitem_does_not_mutate_original():
    """
    Calling HTMLElement.__getitem__ does not mutate the original in
    place.
    """
    original = div["Hello."]
    original["Hi."]
    assert original._children == ["Hello."]  # type: ignore


def test_accepts_any_node_children():
    """Accepts any blu.Node as a child."""
    fragment = Key(2)
    client_element = client(lambda: "Foo")
    assert div[
        client_element,
        div,
        fragment,
        (1, 2, 3),
        [4, 5, 6],
        "Hello",
        7,
        8.0,
        True,
        False,
        None,
    ]._children == [  # type: ignore
        client_element,
        div,
        fragment,
        (1, 2, 3),
        [4, 5, 6],
        "Hello",
        7,
        8.0,
        True,
        False,
        None,
    ]
