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

.. note::
    
    Using square bracket notation on a client element does it mutate the original client element; instead, it returns a copy of the original client element with the new child nodes.

    .. code-block:: python

        from blu import client
        from blu.html import div

        @client
        ClientDiv():
            return div[(yield)]

        original = ClientDiv['ABC']
        copy = original['123']

        original  # <div>ABC</div>
        copy  # <div>123</div>

.. note::

    Using square bracket notation on a client element replaces any existing children rather than appending.

    .. code-block:: python

        from blu import client
        from blu.html import p


        @client
        MyClientElement():
            return p[(yield)]
        

        original = MyClientElement['A', 'B', 'C']
        copy = original[1, 2, 3]

        original  # <p>ABC</p>
        copy  # <p>123</p>

Responding to User Interaction
------------------------------

Use :func:`blu.use_state` to specify UI state and change that state in response to user interaction:

.. code-block:: python

    from blu import use_state


    @client
    def MyClientElement():
        click_count, set_click_count = use_state(0)

        def increment_click_count(e):
            set_click_count(click_count + 1)

        return button(onClick=increment_click_count)[
            'Click Count: ',
            count_count,
        ]

This will result in a button that tells you how many times it's been clicked:

.. todo:: GIF


What's going on here is:

1. We use :func:`use_state <blu.use_state>` to create a state container for the number of clicks whose initial value is 0.
2. :func:`use_state <blu.use_state>` returns a tuple containing the current value and a function that we can use to change the value.
3. We set the onClick attribute of our button element to our *increment_click_count()* function.
4. When the element renders, the current value for the state is 0, so the button will say "Click Count: 0".
5. When the user clicks the button, *increment_click_count()* is called.
6. Within the function body of *increment_click_count()*, *set_click_count()* is called with *click_count + 1* as the new value. *click_count* was 0, so the new value is 1.
7. React sets the state value to 1, and then calls *MyClientElement*'s render function again. This time, the current value is 1, so *click_count* is 1, so the button will say "Click Count: 1".
8. If the user clicks the button again, the current value will again be incremented, and the render function will be called again, resulting in a button that says "Click Count: 2".

.. note::

    use_state is a special type of function used in react called a *hook*. Hooks follow a couple of rules:

    - They must only be used in the scope of client element rendering functions, or in the scope of custom hooks.

    - Within a client element renderer or a custom hook, the same hooks must be called in the same order every time the rendering function or custom hook is called. As long as you don't call hooks in **if** blocks or loops, this condition will be met.

    .. code-block:: python

        from blu import client


        # Wrong!
        @client
        def MyClientElement(some_condition):
            if some_condition:
                value, set_value = use_state(0)
            .
            .
            .
        

        # Wrong!
        @client
        def MyClientElement(some_list_of_numbers):
            for n in some_list_of_numbers:
                item_value, set_item_value = use_state(n)
                .
                .
                .
            .
            .
            .

        # Wrong!
        @client
        def MyClientElement(loop_count)
            i = 0
            while i < loop_count:
                value, set_value = use_state(0)
                i += 1
            .
            .
            .
        

        # Right.
        @client
        def MyClientElement():
            value, set_value = use_state(0)
            .
            .
            .


Directly Manipulating Elements After Rendering
----------------------------------------------

Most of the time, you will be able to get the interactive behavior you want by changing state in response to user interaction. For cases where you need to directly manipulate the DOM, you can use :func:`blu.use_ref`. In the example below, we use :func:`use_ref <blu.use_ref>` to focus an input when the button next to it is clicked.

.. code-block:: python

    from blu import client, use_ref
    from blu.html import div, button, input


    @client
    def MyClientElement():
        input_ref = use_ref()

        def set_focus_to_input(e):
            input_ref[:].focus()
        
        return div[
            button(onClick=set_focus_to_input)['Focus on Input'],
            input(ref=input_ref),
        ]

.. todo:: GIF

What's happening here is:

1. We create a reference object using :func:`use_ref <blu.use_ref>`.
    - A reference object is a box containing a value that doesn't change from render to render unless you explicitly set it.
    - Because we didn't pass any value into :func:`use_ref <blu.use_ref>`, the initial value is :py:data:`None`.

2. We return a div containing:
    - A button that will call *set_focus_to_input()* when clicked, and
    - An input element whose ref is set to the reference object we created. This causes *input_ref*'s value to be set to the rendered input element once rendering is complete.

3. The client element renders the div and its child elements.

4. Because you passed *input_ref* as the *ref* attribute of the input element, the input element that just rendered is set as *input_ref*'s value.

5. If the user clicks the button, *set_focus_to_input()* will be called. *set_focus_to_input()* performs the following steps:
    1. Gets the current value of *input_ref* using ``[:]`` (remember that the current value is the rendered input element).
    2. Calls the *focus()* method on that value. Because the current value is a rendered HTML input element, calling its *focus()* method causes the input element to receive the browser's focus.


