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
        from blu.html import span


        @client
        def ColoredText(color):
            return span(style={'color': color})[(yield)]

    :param renderer: The function that should be used to render the
        :class:`ClientElement <blu.ClientElement>`.

    :return: An element that will be rendered client-side using
        ``renderer``.

    When a :class:`ClientElement <blu.ClientElement>` is rendered, the
    rendering function it was created from is called with whatever
    arguments were passed in using :meth:`ClientElement.__call__()
    <blu.ClientElement.__call__>`:

    .. code-block:: python

        from blu import client
        from blu.html import span


        @client
        def Greeting(name='World'):
            return f'Hello, {name}!'

        
        Greeting('Gary')

    .. code-block:: html

        Hello, Gary!

    If arguments were never set using :meth:`ClientElement.__call__()
    <blu.ClientElement.__call__>`, then the render function will be
    called with no arguments:

    .. code-block:: python
        
        from blu import client
        from blu.html import span


        @client
        def Greeting(name='World'):
            return f'Hello, {name}!'

        
        Greeting

    .. code-block:: html

        Hello, World!

    A render function may use the yield keyword (only once) to get the
    children set using :meth:`ClientElement.__getitem__()
    <blu.ClientElement.__getitem__>`:

    .. code-block:: python

        from blu import client
        from blu.html import span


        @client
        def RedText():
            return span(style={'color': 'red'})[(yield)]


        RedText['Danger!']

    .. code-block:: html

        <span style='color: red'>Danger!</span>

    If the element's children were never set using
    :meth:`ClientElement.__getitem__() <blu.ClientElement.__getitem__>`,
    it won't have any children:

    .. code-block:: python

        from blu import client
        from blu.html import span


        @client
        def RedText():
            return span(style={'color': 'red'})[(yield)]


        RedText

    .. code-block:: html

        <span style='color: red'></span>
    
    """
    element = ClientElement(renderer, (), {}, [])
    if is_client:
        create_proxy(element)  # type: ignore
    return element