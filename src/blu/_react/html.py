"""
A module for generating React HTML elements.

.. code-block:: python

    from html import div, span

    div(id="my-div")[
        span['Hello World!'],
    ]  # <div id="my-div"><span>Hello World!</span></div>
"""

import sys as _sys
import types as _types

from ._types import HTMLElement as _HTMLElement
from ._utils import py_to_html_name as _py_to_html_name


class _HTMLModule(_types.ModuleType):
    
    def __call__(self, tag_name: str) -> _HTMLElement:
        """
        :mod:`blu.html` can be called as a function that takes a tag
        name and returns a :class:`blu.HTMLElement` with that tag name.
        This is an escape hatch for tag names that can't be represented
        as attributes of :mod:`blu.html`:

        .. code-block:: python

            from blu import html

            html('my_tagname-')  # <my_tagname- />
    
        :param tag_name: An HTML tag name.

        :return: A :class:`blu.HTMLElement` with no attributes or child
            nodes, whose tag name is ``tag_name``.
        """
        return _get_element(tag_name)


def __getattr__(tag_name: str) -> _HTMLElement:
    """
    Dynamically generate a :class:`blu.HTMLElement` from a given tag
    name:

    .. code-block:: python

        from blu.html import div

        div(id='my-div')[
            'Hello!',
        ]  # <div id="my-div">Hello!</div>

    :param tag_name: An HTML tag name.

    :return: A :class:`blu.HTMLElement` with no attributes or child
        nodes, whose tag name is ``tag_name``.

    For tag names with dashes, use underscores:

    .. code-block:: python

        from blu.html import my_custom_tagname

        my_custom_tagname  # <my-custom-tagname />
    
    A trailing underscore will be ignored. This allows for elements
    whose tag names are reserved words in Python:

    .. code-block:: python

        from blu.html import del_

        del_  # <del />
    """
    return _get_element(_py_to_html_name(tag_name))
    

def _get_element(tag_name: str) -> _HTMLElement:
    return _HTMLElement(
        tag_name,
        props={},
        children=[],
    )


_this_module = _sys.modules[__name__]
_this_module.__class__ = _HTMLModule

__all__ = [
    
]