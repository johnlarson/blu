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



__all__ = [
    'Node',
    'Element',
    'CustomElement',
    'HTMLElement',
    # 'ReactResponse',
    'is_node',
    'html',
    'import_client',
]