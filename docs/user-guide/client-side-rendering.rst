Client-Side Rendering
=====================

You may have noticed that when you try to set an event handler on an html element like this:

.. code-block:: python

    from blu.html import html, head, body, button


    def __page__():
        return html[
            head,
            body[
                button(onClick=say_hello),
            ],
        ]

    
    def say_hello(e):
        print('Hello!')


visiting the page will result in a 500 error and a message like this in the log:

.. todo:: Add message.

What's going on here is that, under the hood, Blu serializes all of the HTML elements returned from *__page__()* and sends them to the client to be rendered. This means every attribute of every element has to be serializeable.

To solve this, you create a *client element*. A client element is an custom element that is rendered on the client.

.. code-block:: python

    from blu import client
    from blu.html import html, head, body, button


    def __page__():
        return html[
            head,
            body[
                HelloButton,
            ],
        ]

    
    @client
    def HelloButton():
        return button(onClick=say_hello)


    def say_hello():
        print('Hello!')

So if you visit the page in the example above,

1. The server tells the client to render an html tag with a head element and body element in it, with a HelloButton element in the body.

2. The client then renders those elements.
    - The client already knows how to render the html, head, and body elements, since they are native HTML elements.
    - The client renders the HelloButton element by running the function you decorated with the :func:`client <blu.client>` decorator.

So your page renders as:

.. code-block:: html

    <html>
        <head></head>
        <body>
            <button></button>
        </body>
    </html>

with an event listener attached to the button that prints "Hello!" to the web browser's developer console when the button is clicked.

.. note::
    
    Client elements cannot be created from asynchronous functions.

    .. code-block:: python

        from blu import client
        from blu.html import p

        # Wrong!
        @client
        async def Hello():
            return p['Hello, World!']

        
        # Right.
        @client
        def Hello():
            return p['Hello, World!']


.. note::

    Client-side code runs in a different environment than server-side code. If your client-side code uses an external library, make sure it is installed in the client environment by adding it to the list of client dependencies in ``app/__settings__.py`` (if the ``__settings__.py`` doesn't exist, create it)::

        app/
          __index__.py
          __settings__.py

    .. code-block:: python
        :caption: app/__index__.py

        import arrr


        def __page__():
            return p[
                arrr.translate('Hello there. How are you?')
            ]


    .. code-block:: python
        :caption: app/__settings__.py

        CLIENT_REQUIREMENTS = ['arrr']


.. note::

    Client-side code runs in a different environment than server-side code. If your client-side code uses dependencies that aren't available on the server, make sure you check the environment before importing those dependencies:

    .. code-block:: python
        :caption: Wrong!
        :emphasize-lines: 4

        from blu import client
        from blu.html import button
        
        from pyscript import window


        def __page__():
            return GoToPyPIButton

        
        @client
        def GoToPythonDotOrgButton():
            return button(onClick=navigate_to_python_dot_org)

        
        def navigate_to_python_dot_org(e):
            window.location = 'https://www.python.org'

    .. code-block:: python
        :caption: Right.
        :emphasize-lines: 4-5

        from blu import client
        from blu.html import button
        
        if client:
            from pyscript import window


        def __page__():
            return GoToPyPIButton

        
        @client
        def GoToPythonDotOrgButton():
            return button(onClick=navigate_to_python_dot_org)

        
        def navigate_to_python_dot_org(e):
            window.location = 'https://www.python.org'


Passing Arguments to Client Elements
------------------------------------


Client elements can take arguments:

.. code-block:: python

    from blu import client
    from blu.html import span


    def __page__():
        ColoredText('red', text='This should be red.')

    
    @client
    def ColoredText(color, text='Hello, World!'):
        return span(style={'color': color})[text]

.. note:: Calling a client element as a function does not immediately result in its rendering function being called; that call is deferred until the element is rendered on the client.

.. note::
    
    Calling a client element as a function does it mutate the original client element; instead, it returns a copy of the original client element with the new render arguments.

    .. code-block:: python

        from blu import client
        from blu.html import p

        @client
        Greeting(name):
            return p[f'Hello, {name}!']

        original = Greeting('Adam')
        copy = original('Brittany')

        original  # <p>Hello, Adam!</p>
        copy  # <p>Hello, Brittany!</p>

.. note::

    Calling a client element as a function completely replaces any existing render arguments.

    .. code-block:: python

        from blu import client
        from blu.html import p


        @client
        MyClientElement(a, b=2):
            return p[f'{a},{b}']
        

        original = MyClientElement(3, b=4)
        copy = original(1)

        original  # <p>3,4</p>
        copy  # <p>1,2</p>


Passing Children to Client Elements
-----------------------------------

You can also pass child nodes to client elements using square bracket notation and access them in the rendering function with the *yield* keyword:

.. code-block:: python

    from blu import client
    from blu.html import span


    def __page__():
        ColoredText('red')[
            'This should be red.',
        ]

    
    @client
    def ColoredText(color):
        return span(style={'color': color})[
            (yield),
        ]