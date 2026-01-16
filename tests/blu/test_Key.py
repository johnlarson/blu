from blu import Key, client

from blu.html import div, span
from tests.utils import node_eq, renders_as


def test_uses_key():
    """The key passed in is used."""
    fragment = Key(3)
    assert fragment._key == 3  # type: ignore


def renders_children():
    """Renders as its children."""
    assert renders_as(Key(3)[div['Hello']], div['Hello'])


def test_no_children():
    """
    Rendering a Key that never had children added using __getitem__ will
    result in nothing being rendered where the Key appears.
    """
    assert renders_as(Key(3), ())


def test_replace_children():
    """
    When Key.__getitem__ is called, the resulting copy does not retain
    the original's children.
    """
    assert node_eq(Key(3)[div][span], Key(3)[span])


def test_getitem_retains_key():
    """
    When Key.__getitem__ is called, the resulting copy has the same key
    as the original.
    """
    original = Key(3)
    assert original._key == original[div]._key  # type: ignore


def test_getitem_does_not_mutate_original():
    """Key.__getitem__ does not mutate the original in place."""
    original = Key(3)[div]
    original[span]
    assert node_eq(original, Key(3)[div])


def test_accepts_any_node_children():
    """Accepts any blu.Node as a child."""

    @client
    def Foo():
        return 'Foo'
    
    assert renders_as(
        Key(4)[
            Foo,
            div,
            Key(2),
            (1, 2, 3),
            [4, 5, 6],
            'Hello',
            7,
            8.0,
            True,
            False,
            None,
        ],
        (
            'Foo',
            div,
            '123456Hello78.0truefalse',
        ),
    )


def test_accepts_children_with_children():
    """Renders correctly with element children that have children."""
    assert renders_as(Key(1)[Key(2)['Hello!']], 'Hello!')
