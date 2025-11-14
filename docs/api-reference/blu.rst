``blu``
=======

.. todo::

    Document the following:

    - ElementRenderer?
    - Ref
    - Response
    - WrongEnvironmentError
    - app
    - client
    - create_rare_html_element
    - is_client
    - use_effect
    - use_state
    - use_ref 

.. automodule:: blu
    :exclude-members: HTMLElement, ClientElement, Key, Ref

    .. autoclass:: ClientElement()
        :special-members: __call__, __getitem__

    .. autoclass:: HTMLElement()
        :special-members: __call__, __getitem__

    .. autoclass:: Key
        :special-members: __getitem__

    .. autoclass:: Ref
        :special-members: __getitem__, __setitem__


.. py:type:: Node
    :canonical: ClientElement | HTMLElement | Key | Iterable[Node] | str | int | float | bool | None

    A valid child of a React element. Nodes are rendered as follows:
          
    - A :class:`blu.HTMLElement` is rendered as described `here <https://react.dev/reference/react-dom/components>`_.

        .. code-block:: python

            from blu.html import span

            span(id='my-id')['Hello, World!']

        .. code-block:: html

            <span id="my-id">Hello, World!</span>
    
    - A :class:`blu.ClientElement` is rendered as the return value of its rendering function. See :class:`blu.ClientElement` for more details.
        .. code-block:: python

            from blu import client
            from blu.html import span


            @client
            def WorldGreeting():
                return span['Hello, World!']


            WorldGreeting
        
        .. code-block:: html

            <span>Hello, World!<span>
    
    - A :class:`blu.Key` is rendered as a keyed `React fragment <https://react.dev/reference/react/Fragment>`_ whose key is the same as the key passed in to the :class:`Key <blu.Key>` object's constructor.

        .. code-block:: python

            from blu import Key

            Key(125)[
                span['Hello, World!'],
            ]

        .. code-block:: html

            <span>Hello, World!</span>

    - A :py:class:`str` is rendered as an HTML text node.

        .. code-block:: python

            'Hello, World!'

        .. code-block:: html

            Hello, World!

    - A :py:class:`tuple` is rendered as a `React fragment <https://react.dev/reference/react/Fragment>`_ without a key.

        .. code-block:: python

            ('Hello,', ' ', 'World!')

        .. code-block:: html

            Hello, World!

    - Any other :py:class:`Iterable <collections.abc.Iterable>` is rendered in React as JavaScript arrays.

        .. code-block:: python

            ['Hello,', ' ', 'World!']

        .. code-block:: html

            Hello, World!
    
    - A :py:class:`int` is rendered as an HTML text node.

        .. code-block:: python

            1
        
        .. code-block:: html

            1
        
    - A :py:class:`float` is rendered as an HTML text node.

        .. code-block:: python

            1.0

        .. code-block:: html

            1.0
        
    - :py:data:`True` is rendered as an HTML text node with the text ``true``.

        .. code-block:: python

            True
        
        .. code-block:: html

            true
        
    - :py:data:`False` is rendered as an HTML text node with the text ``false``.

        .. code-block:: python

            False

        .. code-bock:: html

            false
        
    - :py:data:`None` is rendered as nothing. It is rendered in React as the JavaScript ``null`` value.

        .. code-block:: python

            None

        .. code-block:: html

