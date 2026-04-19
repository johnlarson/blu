import pytest
from blu import client, Key
from blu.html import div


def test_args():
    """
    Calling a ClientElement as a function returns a copy whose `_args`
    attribute is the provided positional arguments as a tuple.
    """

    @client
    def Hello(first_name, last_name):
        return f"Hello, {first_name} {last_name}!"

    assert Hello("Amanda", "Myers")._args == ("Amanda", "Myers")  # type: ignore


def test_kwargs():
    """
    Calling a ClientElement as a function returns a copy whose `_kwargs`
    attribute is the given keyword arguments as a dict.
    """

    @client
    def Hello(first_name, last_name):
        return f"Hello, {first_name} {last_name}!"

    assert Hello(first_name="Amanda", last_name="Myers")._kwargs == {  # type: ignore
        "first_name": "Amanda",
        "last_name": "Myers",
    }


def test_args_and_kwargs():
    """
    Caling a ClientElement with positional and keyword arguments will
    result in a copy whose _args attribute is the given positional
    arguments and whose _kwargs attribute is the given keyword
    arguments.
    """

    @client
    def Hello(first_name, last_name):
        return f"Hello, {first_name} {last_name}!"

    element = Hello("Amanda", last_name="Myers")
    assert element._args == ("Amanda",)  # type: ignore
    assert element._kwargs == {"last_name": "Myers"}  # type: ignore


def test_no_args_or_children():
    """
    The ClientElement return from the @client decorator will have an
    _args attribute of () and _kwargs attribute of {}
    """

    @client
    def Hello():
        return f"Hello!"

    assert Hello._args == ()  # type: ignore
    assert Hello._kwargs == {}  # type: ignore


def test_replace_original_args_and_kwargs():
    """
    When a ClientElement is called as a function to create a copy, none
    of the original positional or keyword arguments will be retained in
    the copy.
    """

    @client
    def E(a, b=0, c=0):
        return (a, b, c)

    original = E(1, 2, c=3)
    original(4)
    assert original._args == (1, 2)  # type: ignore
    assert original._kwargs == {"c": 3}  # type: ignore


def test_key():
    """
    Passing the keyword argument "key" into a ClientElement's __call__
    method results in ClientElement that has the provided key.
    """

    @client
    def E():
        return "Hello."

    assert E(key=3)._get_key() == 3


def test_call_replaces_key():
    """
    If a "key" keyword argument is specified in ClientElement.__call__,
    that will be the key of the resulting copy, regardless of what the
    original key was.
    """
    assert client(lambda: "Hello")(key=1)(key=2)._get_key() == 2


def test_call_does_not_retain_key():
    """
    If no key is specified in a call to ClientElement.__call__, the
    resulting copy will not have a key, even if the original did.
    """
    with pytest.raises(LookupError):
        client(lambda: "Hello")(key=1)()._get_key()


def test_call_retains_children():
    """
    When a ClientElement is called as a function, the resulting copy has
    the same children as the original.
    """

    @client
    def Foo(a):
        return (yield), a

    assert Foo[1](2)._children == [1]  # type: ignore


def test_call_does_not_mutate_original():
    """
    Calling a ClientElement as a function does not mutate the original
    in place.
    """
    original = client(lambda x: x)(1)
    original(2)
    assert original._args == (1,)  # type: ignore


def test_children():
    """
    __getitem__ returns a copy whose children are the items passed in,
    as a list.
    """

    @client
    def Foo():
        return div[(yield)]

    assert Foo["Hello", "There"]._children == ["Hello", "There"]  # type: ignore


def test_no_children():
    """
    If an element's children are not set, its _children attribute will
    be [].
    """

    @client
    def Foo():
        return div[(yield)]

    assert Foo._children == []  # type: ignore


def test_doesnt_take_children():
    """
    When a ClientElement doesn't accept children, i.e. its rendering
    function has no yield statement, calling __getitem__ raises a
    TypeError.
    """
    Foo = client(lambda x: x)
    with pytest.raises(TypeError):
        Foo["Hello"]


def test_replace_children():
    """
    When ClientElement.__getitem__ is called, the resulting copy does
    not retain the original's children.
    """

    @client
    def Foo():
        return (yield)

    assert Foo[1, 2, 3][4, 5, 6]._children == [4, 5, 6]  # type: ignore


def test_getitem_retains_original_args_and_kwargs():
    """
    When ClientElement.__getitem__ is called, the resulting copy has the
    same positional and keyword render arguments as the original.
    """

    @client
    def Foo(x, y):
        return x, (yield)

    element = Foo(1, y=2)[3]
    assert element._args == (1,)  # type: ignore
    assert element._kwargs == {"y": 2}  # type: ignore


def test_getitem_retains_key():
    """
    When ClientElement.__getitem__ is called, the resulting copy has the
    same key as the original.
    """

    @client
    def Foo():
        return (yield)

    assert Foo(key=0)[1]._get_key() == 0


def test_getitem_does_not_mutate_original():
    """
    ClientElement.__getitem__ does not mutate the original in place.
    """

    @client
    def Foo():
        return (yield)

    original = Foo[1]
    original[2]
    assert original._children == [1]  # type: ignore


def test_accepts_any_node_children():
    """Accepts any blu.Node as a child."""

    @client
    def Foo():
        return (yield)

    @client
    def Bar():
        return "Bar"

    fragment = Key(2)

    assert Foo[
        Bar,
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
        Bar,
        div,
        fragment,
        (1, 2, 3),
        [4, 5, 6],
        "Hello",
        7,
        "8.0",
        "True",
        "False",
        None,
    ]
