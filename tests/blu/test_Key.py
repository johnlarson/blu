from blu import Key, client

from blu.html import div, span
from tests.utils import node_eq, renders_as


def test_uses_key():
    """The key passed in is used."""
    fragment = Key(3)
    assert fragment._key == 3  # type: ignore


def stores_children():
    """Stores children as list in _children attribute."""
    assert Key(3)["Hello"]._children == ["Hello"]  # type: ignore


def test_no_children():
    """If no children are set, _children attribute is []."""
    assert Key(3)._children == []  # type: ignore


def test_replace_children():
    """
    When Key.__getitem__ is called, the resulting copy does not retain
    the original's children.
    """
    assert Key(3)[div][span]._children == [span]  # type: ignore


def test_getitem_retains_key():
    """
    When Key.__getitem__ is called, the resulting copy has the same key
    as the original.
    """
    original = Key(3)
    assert original[div]._key == 3  # type: ignore


def test_getitem_does_not_mutate_original():
    """Key.__getitem__ does not mutate the original in place."""
    original = Key(3)[div]
    original[span]
    assert original._children == [div]  # type: ignore


def test_accepts_any_node_children():
    """Accepts any blu.Node as a child."""

    @client
    def Foo():
        return "Foo"

    fragment = Key(2)

    Key(4)[
        Foo,
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
        Foo,
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
