from blu._react.types import ClientElement, ElementRenderer


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
    
    def __call__(
        self,
        render_function: ElementRenderer[...],
    ) -> ClientElement[object]:
        ...
    
    def __bool__(self) -> bool:
        ...


client = ...
"""
Creates client-rendered custom components.

Can also be used to test whether currently running in a client
environment.
"""

