``blu``
=======

.. todo::

    Typing for:

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

    .. autodata:: app
        :no-value:

        An `ASGI <https://asgi.readthedocs.io/en/latest/>`_ app that runs the Blu application defined in your current Python environment's ``app`` package (for most ASGI servers, running the server in the parent directory of your project's ``app`` directory will put your project's ``app`` package in the Python environment).

        .. code-block:: console
   
            $ uvicorn blu:app

        .. code-block:: console
   
            $ hypercorn blu:app

        .. code-block:: console
   
            $ daphne blu:app
    
    .. py:data:: is_client
        :annotation: bool

        ``True`` if running in a web browser environment, ``False`` if running in server environment.

        .. code-block:: python

            from blu import is_client

            if is_client:
                print('Hello from your web browser!')
            else:
                print('Hello from your web app server!')
        

    .. py:type:: ClientRenderer
        :canonical: collections.abc.Callable[..., blu.Node | Generator[None, Node, Node]]

        A function that defines how a :class:`ClientElement <blu.ClientElement>` is rendered. This type of function is passed into the :func:`client <blu.client>` decorator to create a :class:`ClientElement <blu.ClientElement>`:

        .. code-block:: python

            from blu import client
            from blu.html import span


            @client
            def Greeting():
                return 'Hello, World!'

        For more details on how :type:`ClientRenderer <blu.ClientRenderer>` functions are used, see :func:`client() <blu.client>`.

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

            .. code-block:: html

                false
            
        - :py:data:`None` is rendered as nothing. It is rendered in React as the JavaScript ``null`` value.

            .. code-block:: python

                None

            .. code-block:: html

.. _note-on-hooks:
Note on Hooks
-------------

.. include:: /_includes/hooks.rst