import platform
from blu._react.types import ClientElement, ElementRenderer
from blu._utils.client import is_client

if is_client:
    from pyscript.ffi import create_proxy  # type: ignore


class ClientDecorator:
    """
    The type of :func:`blu.client`. Can be used as a decorator to denote
    that an element's rendering should be deferred to the client or as a
    test for whether the code is currently running in a client
    environment.

    .. code-block:: python

        from blu import client
        from blu.html import p

        if client:
            import pyscript

        
        @client
        def MyClientElement():
            return p['Hello World!']
    """
    
    def __call__[**P](
        self,
        renderer: ElementRenderer[P],
    ) -> ClientElement:
        element = ClientElement(renderer, (), {}, [])
        if is_client:
            create_proxy(element)  # type: ignore
        return element
    
    def __bool__(self) -> bool:
        return is_client


client = ClientDecorator()
"""
Creates client-rendered custom components.

Can also be used to test whether currently running in a client
environment.
"""

