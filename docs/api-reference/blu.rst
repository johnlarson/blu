``blu``
=======

.. todo::

    Document the following:

    - HTMLElement
    - app
    - Node
    - Response
    - client
    - ClientElement
    - use_state
    - use_ref
    - use_effect
    - Settings
    - ClientDecorator
    - Effect
    - Ref
    - ElementRenderer

.. automodule:: blu
    :exclude-members: HTMLElement, ClientDecorator, ClientElement, Ref, ClientDecorator, client

    .. autoclass:: HTMLElement()
        :special-members: __call__, __getitem__

    .. autoclass:: ClientDecorator
        :special-members: __call__, __bool__

    .. autoclass:: ClientElement
        :special-members: __call__, __getitem__

    .. autoclass:: Ref
        :special-members: __getitem__

    .. autofunction:: client
    
.. py:type:: Node
    :canonical: None | bool | int | float | str | HTMLElement | ClientElement | tuple[Node, ...] | collections.abc.Iterable[Node]

    A valid child of a React element.

.. py:type:: ElementRenderer[**P]
    :canonical: collections.abc.Callable[P, Node | collections.abc.Generator[None, Node, Node] | collections.abc.AsyncGenerator[None | Node, Node]]

    A function that renders a custom element as native HTML nodes.

    :param P: The arguments accepted by the custom element type this function renders.

    :return: A :class:`blu.HTMLElement` for which all descendant nodes are
        native HTML nodes.