from pathlib import Path as _Path

from blu._react.types import (
    Node, Element, CustomElement, HTMLElement, is_node
)
from blu._react import html
# from ._http import ReactResponse


def import_client(path: str | _Path, name: str = 'default') -> CustomElement:
    """
    Import a client React component for use in a page.

    :param path: The path to the JavaScript module that contains the
        component, relative to the directory where the ``app`` python
        module's source is.
    :param name: The export name of the component in the JavaScipt
        module.

    :return: A :class:`CustomElement` whose
        :attr:`path <CustomElement.path>` is ``path`` and whose
        :attr:`name <CustomElement.name>` is ``name``.
    """
    return CustomElement(path, name, props={}, children=[])


def create_html_element(tagname: str) -> HTMLElement:
    """
    Create an HTML element. Usually, you will use the :mod:`blu.html`
    module to create HTML elements, but in rare cases where you cannot
    import the tag name you need from :mod:`blu.html`, you can use this
    function to create an HTML element from any valid tag name.

    .. code-block:: python

        from blu import create_rare_html_element

        my_element = create_rare_html_element('my_element-')

        my_element(id='my-id')['Hello, World!']
    
        
    .. code-block:: html

        <my_element->Hello, World!</my_element->

    :param tagname: A valid HTML tag name.
    :return: A :class:`blu.HTMLElement` whose tag name is ``tagname``,
        with no props set.
    """
    ...



__all__ = [
    'Node',
    'Element',
    'CustomElement',
    'HTMLElement',
    # 'ReactResponse',
    'create_html_element',
    'is_node',
    'html',
    'import_client',
]