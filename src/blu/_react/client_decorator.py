import platform
from blu._react.types import ClientElement, ElementRenderer
from blu._utils.client import is_client

if is_client:
    from pyscript.ffi import create_proxy  # type: ignore


def client[**P](renderer: ElementRenderer[P]) -> ClientElement:
    """
    Decorator that converts a rendering function into a
    :class:`blu.ClientElement`.

    .. code-block:: python

        from blu import client
        from blu.html import p

        if client:
            import pyscript

        
        @client
        def MyClientElement():
            return p['Hello World!']
    

    :param renderer: The function that should be used to render the
        :class:`ClientElement`<blu.ClientElement>.

    :return: An element that will be rendered client-side using
        ``renderer``.
    """
    element = ClientElement(renderer, (), {}, [])
    if is_client:
        create_proxy(element)  # type: ignore
    return element