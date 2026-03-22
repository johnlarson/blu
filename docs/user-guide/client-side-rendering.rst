Client-Side Rendering
=====================

You may have noticed that when you try to set an event handler on an html element like this:

.. code-block:: python

    from blu.html import html, head, body, button


    def __page__():

        def say_hello(e):
            print('Hello!')
        
        return html[
            head,
            body[
                button(onClick=say_hello),
            ],
        ]


visiting the page will result in a 500 error and a message like this in the log:

.. code-block:: none

    blu._exceptions.WrongEnvironmentError: Could not add
    attribute "onClick" to button element. Event-handling
    attributes like "onClick" can only be set in client-side
    rendering; this code was run server-side.

What's going on here is that, under the hood, Blu pickes all of the HTML elements returned from *__page__()* and sends them to the client to be rendered. This means every attribute of every element has to be pickleable.

To solve this, you create a *client element*. A client element is an custom element that is rendered on the client.

.. code-block:: python

    from blu import client
    from blu.html import html, head, body, button

    __client__ = True


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


    def say_hello(e):
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

.. include:: /_includes/client-side-rendering-notes.rst


Passing Arguments to Client Elements
------------------------------------

Client elements can take arguments:

.. code-block:: python

    from blu import client
    from blu.html import span

    __client__ = True


    def __page__():
        return ColoredText('red', text='This should be red.')

    
    @client
    def ColoredText(color, text='Hello, World!'):
        return span(style={'color': color})[text]


.. include:: /_includes/client-element-call-notes.rst


Passing Children to Client Elements
-----------------------------------

You can also pass child nodes to client elements using square bracket notation and access them in the rendering function with the *yield* keyword:

.. code-block:: python

    from blu import client
    from blu.html import span

    __client__ = True


    def __page__():
        return ColoredText('red')[
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

        __client__ = True


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

        __client__ = True


        @client
        MyClientElement():
            return p[(yield)]
        

        original = MyClientElement['A', 'B', 'C']
        copy = original[1, 2, 3]

        original  # <p>ABC</p>
        copy  # <p>123</p>

Hooks
-----

.. include:: /_includes/hooks.rst

Responding to User Interaction
------------------------------

Use :func:`blu.use_state` to specify UI state and change that state in response to user interaction:

.. code-block:: python

    from blu import client, use_state
    from blu.html import button

    __client__ = True


    @client
    def MyClientElement():
        click_count, set_click_count = use_state(0)

        def increment_click_count(e):
            set_click_count(click_count + 1)

        return button(onClick=increment_click_count)[
            'Click Count: ',
            click_count,
        ]

This will result in a button that tells you how many times it's been clicked:

.. figure:: /_img/responding_to_user_interaction.gif


What's going on here is:

1. We use :func:`use_state <blu.use_state>` to create a state container for the number of clicks whose initial value is 0.
2. :func:`use_state <blu.use_state>` returns a tuple containing the current value and a function that we can use to change the value.
3. We set the onClick attribute of our button element to our *increment_click_count()* function.
4. The first time the element renders, the current value for the state is 0, so the button will say "Click Count: 0".
5. When the user clicks the button, *increment_click_count()* is called.
6. Within the function body of *increment_click_count()*, *set_click_count()* is called with *click_count + 1* as the new value. *click_count* was 0, so the new value is 1.
7. React sets the state value to 1, and then calls *MyClientElement*'s render function again. This time, the current value is 1, so *click_count* is 1, so the button will say "Click Count: 1".
8. If the user clicks the button again, the current value will again be incremented, and the render function will be called again, resulting in a button that says "Click Count: 2".

.. note:: :func:`use_state <blu.use_state>` is a special type of function used in React called a *hook*. There are specific rules you have to follow when using hooks. See :ref:`Hooks` for more details.


Directly Manipulating Rendered Elements
---------------------------------------

Most of the time, you will be able to get the interactive behavior you want by changing state in response to user interaction. For cases where you need to directly manipulate the DOM, you can use :func:`blu.use_ref`. In the example below, we use :func:`use_ref <blu.use_ref>` to focus an input when the button next to it is clicked.

.. code-block:: python

    from blu import client, use_ref
    from blu.html import div, button, input

    __client__ = True


    @client
    def MyClientElement():
        input_ref = use_ref()

        def set_focus_to_input(e):
            input_ref[:].focus()
        
        return div[
            button(onClick=set_focus_to_input)['Focus on Input'],
            input(ref=input_ref),
        ]

.. figure:: /_img/directly_manipulating_rendered_elements.gif

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

.. note:: :func:`use_ref <blu.use_ref>` is a special type of function used in React called a *hook*. There are specific rules you have to follow when using hooks. See :ref:`Hooks` for more details.


Performing an Action Immediately After Rendering
------------------------------------------------

Sometimes, you'll want to perform some action immediately after rendering, without waiting for user interaction. For these cases, use :func:`blu.use_effect`. For example, maybe we want to trigger an alert modal once the element is rendered:

.. code-block:: python

    from blu import client, is_client, use_effect
    from blu.html import p

    if is_client:
        from js import alert

    __client__ = True


    @client
    def MyClientElement():

        @use_effect
        def send_alert():
            alert(
                'Hello, there! Nothing to report; just wanted to say '
                'hi. Have a nice day!'
            )
        
        return p['(element content)']

.. figure:: /_img/perform_an_action_immediately_after_rendering.gif

What's happening here:

1. On the client side only, we import the *alert()* function from the *js* module. The *js* module is automatically made available in client-side code in Blu apps, and does not need to be installed. It provides access to the global JavaScript scope of the page.
2. We use :func:`use_effect <blu.use_effect>` to tell React to call *send_alert()* right after rendering.
3. We return a paragraph element that just says "(element content)".
4. The client element renders based as the return value of its rendering function, a paragraph element with the text "(element content)".
5. Immediately after rendering, *send_alert()* is called.
6. *send_alert()* calls *alert()* with a message.
7. This causes an alert modal to pop up in front of the page with the provided message.
8. The user can then dismiss the alert modal.

.. note:: :func:`use_effect <blu.use_effect>` is a special type of function used in React called a *hook*. There are specific rules you have to follow when using hooks. See :ref:`Hooks` for more details.

.. note::

    If your effect has lingering side effects, make sure you clean up after yourself. To do so, use the **yield** keyword after your setup code, followed by your cleanup code:

    .. code-block:: python

        from blu import client, is_client, use_effect, use_state
        from blu.html import button

        if is_client:
            # The js module provides access to JavaScript APIs. See
            # Blu's API reference for more details.
            from js import alert

        __client__ = True


        @client
        def EffectWithCleanup():
            render_count, set_render_count = use_state(1)

            @use_effect
            def _():
                alert(f'SETUP {render_count}')
                yield
                alert(f'TEARDOWN {render_count}')

            def handle_button_click(e):
                set_render_count(render_count + 1)

            return button(onClick=handle_button_click)["Rerender"]

    .. figure:: /_img/effect_cleanup.gif

Accessing Server-Side Resources from the Client
-----------------------------------------------

Sometimes you'll need to access server-side resources after a page has loaded, usually in response to user input. You can do using the :func:`@blu.server` decorator, which exposes a server-side function to be called client-side.

.. code-block:: python
    :caption: app/hello_module.py

    from blu import server


    @server
    def hello():
        print('Hello!')


.. code-block:: python
    :caption: app/client.py

    from blu import client
    from blu.html import div

    from app.hello_module import hello

    __client__ = True


    @client
    def SayHello():
        return div[hello()]


.. code-block:: html

    <div>Hello!</div>

.. danger::

    Don't use this in production. The only exception to this rule is when:

    1. The server function doesn't change any persistent state (no writing files, updating databases, etc.), *AND*
    2. The server function does not return any sensitive data.

    The :func:`@server <blu.server>` function security strategy is still being planned and has not been implemented.

.. note::
    When calling a :func:`@server <blu.server>` function clientside, all arguments must be JSON-serializable, and the return value must be `picklable <https://docs.python.org/3/library/pickle.html>`_.

    .. code-block:: python
        :caption: Wrong! (non-JSON-serializable argument)

        @client
        def ClientElement():
            return div[my_server_function(object())]

    .. code-block:: python
        :caption: Wrong! (non-picklable return value)

        @server
        def my_server_function():
            def my_callable():
                return 1
            return my_callable

    .. code-block:: python
        :caption: Right.

        class A:
            def __init__(self, value):
                self.value = value


        @server
        def my_server_function(json_input):
            return A(json_input)

        
        @client
        def ClientElement():
            return my_server_function({'Hello': 'World'})


.. note::
    A :func:`@server <blu.server>` function must be defined at the top level of a module.

    .. code-block:: python
        :caption: Wrong!

        class A:

            @server
            def func():
                return 1

    
    .. code-block:: python
        :caption: Wrong!

        def func_factory():

            @server
            def func():
                return 1
            
            return func
        
    .. code-block:: python
        :caption: Right.

        @server
        def func():
            return 1