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

.. automodule:: blu
    :exclude-members: HTMLElement, ClientDecorator, ClientElement, Element

    .. autoclass:: HTMLElement()
        :special-members: __call__, __getitem__

    .. autoclass:: ClientDecorator
        :special-members: __call__, __bool__

    .. autoclass:: ClientElement
        :special-members: __call__, __getitem__
    
    .. autoclass:: Element
        :special-members: __call__, __getitem__

.. py:type:: Node
    :canonical: HTMLElement | str

    A valid child of a React element.