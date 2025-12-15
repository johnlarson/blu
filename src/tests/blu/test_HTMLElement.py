from blu._react.client_decorator import client
from blu._react.types import Key
from blu.html import div, span
from tests.utils import node_eq, renders_as


def test_kwarg_props():
    """
    Keyword arguments passed into HTMLElement.__call__ are passed as
    props when the HTMLElement is rendered.
    """
    assert div(id=3)._attrs['id'] == 3


def test_trailing_underscore():
    """
    When a keyword argument to HTMLElement.__call__ has a trailing
    underscore in the argument name, the trailing underscore will not
    appear in the resulting React HTML element.
    """
    assert div(id_=3)._attrs['id'] == 3


def test_non_trailing_underscore():
    """
    When a keyword argument to HTMLElement.__call__ has a non-trailing
    underscore in the argument name, the underscore will be converted to
    a dash in the resulting React HTML element.
    """
    assert div(data_count=3)._attrs['data-count'] == 3


def test_props_dict():
    """
    When a dict is passed as the first positional argument to
    HTMLElement.__call__, its keyword-value pairs are passed as props
    to the resulting React HTML element.
    """
    assert div({'my_-attr_': 3})._attrs['my_-attr_'] == 3


def test_props_dict_kwargs_conflicts():
    """
    If there is a conflict between the positional argument dict and the
    keyword arguments in HTMLElement.__call__, the positional argument
    will take precedence.
    """
    assert div({'id': 1}, id=2)._attrs['id'] == 2


def test_replace_original_props():
    """
    When HTMLElement.__call__ is called, the resulting HTMLElement will
    not include the original's props, other than children.
    """
    assert node_eq(div(id=1)(id=2), div(id=2))


def test_call_retains_children():
    """
    When HTMLElement.__call__ is called, the resulting HTMLElement will
    have the same children as the original.
    """
    assert node_eq(div['Hello!'](id=1), div(id=1)['Hello!'])


def test_call_does_not_mutate_original():
    """
    Calling HTMLElement.__call__ does not mutate the original in place.
    """
    original = div(id=1)
    original(id=2)
    assert original._attrs['id'] == 1


def test_children():
    """
    Calling HTMLElement.__getitem__ returns a copy whose children are
    the Nodes passed into the square brackets.
    """
    assert div[1, 2, 3]._children == [1, 2, 3]


def test_no_children():
    """
    An HTMLElement with no children will render as an HTML element with
    no children.
    """
    assert div._children == []


def test_replace_children():
    """
    When HTMLElement.__getitem__ is called, the returned copy will not
    retain the original's children.
    """
    assert node_eq(div[1, 2, 3][4, 5, 6], div[4, 5, 6])


def test_getitem_retains_original_props():
    """
    When HTMLElement.__getitem__ is called, the returned copy will have
    the same non-children props as the original.
    """
    assert div(id=1)['Hello']._attrs['id'] == 1


def test_getitem_does_not_mutate_original():
    """
    Calling HTMLElement.__getitem__ does not mutate the original in
    place.
    """
    original = div['Hello.']
    original['Hi.']
    assert node_eq(original, div['Hello.'])


def test_accepts_any_node_children():
    """Accepts any blu.Node as a child."""
    assert renders_as(
        div[
            client(lambda: 'Foo'),
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
        div[
            'Foo',
            div,
            '123456Hello78.0truefalse',
        ],
    )


def test_accepts_children_with_children():
    """Renders correctly with element children that have children."""
    @client
    def Foo():
        return span[(yield)]
    
    assert renders_as(
        div[Foo['Hello']],
        div[span['Hello']],
    )


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