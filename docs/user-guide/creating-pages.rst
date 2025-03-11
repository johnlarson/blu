.. _creating-pages:

Creating Pages
==============

The :ref:`Quickstart` guide shows how to make a simple page using Blu.

This section goes into greater depth on how to generate user interfaces using Blu.


HTML Elements
-------------

The :ref:`Quickstart` guide shows how to make a simple page with html, head, and body elements:

.. code-block:: python

    from blu.html import body, head, html


    def __page__():
        return html[
            head,
            body['Hello World!'],
        ]

You can import any HTML tag from :mod:`blu.html`:

.. code-block:: python

    from blu.html import (
        html, head, body, div, span, select, canvas, mymadeuptagname
    )

    html[
        head,
        body[
            div,
            span,
            select,
            canvas,
            mymadeuptagname,
        ],
    ]

.. code-block:: html

    <html>
        <head></head>
        <body>
            <div></div>
            <span></span>
            <select></select>
            <canvas></canvas>
            <mymadeuptagname></mymadeuptagname>
        </body>
    </html>

If the HTML tag name you want to import is not a valid Python identifier or is a reserved word in Python, you can use the builtin :py:func:`getattr` function:

.. code-block:: python

    import blu.html

    del_ = getattr(blu.html, 'del')
    tag_name_with_dashes = getattr(blu.html, 'tag-name-with-dashes')

    tag_name_with_dashes[
        del_['Hello, World!'],
    ]

.. code-block:: html

    <tag-name-with-dashes>
        <del>Hello, World!</del>
    </tag-name-with-dashes>


HTML Attributes
+++++++++++++++

You can set the HTML attributes of an element by calling it as a function:

.. code-block:: python

    from blu.html import div

    div(id='my-id')

.. code-block:: html

    <div id="my-id"></div>

.. note::

    Calling an HTML element as a function does not mutate the original; instead, it returns a copy with the new attributes.

    .. code-block:: python

        from blu.html import div

        without_attributes = div
        with_attributes = div(a='1', b='2')

        without_attributes  # <div></div>
        with_attributes  # <div a="1" b="2"></div>

.. note::

    When you set HTML attributes on an element, you completely replace the existing attributes, rather than adding attributes on top:

    .. code-block:: python

        from blu.html import div

        original = div(a='1', b='2')
        
        original(c='3', d='4')  # <div c="3" d="4"></div>

.. note::

    Blu HTML elements take the same attributes as React HTML elements, not native HTML elements (see https://react.dev/reference/react-dom/components for more information):

    .. code-block:: python

        # Wrong!
        div(class='my-class')

        # Right.
        div(className='my-class')


.. note::

    Event-handling attributes like "onClick" are only supported in client-side rendering (see :ref:`Client-Side Rendering` for more details).

    .. code-block:: python

        from blu.html import div

        def log_clicked(e):
            print('Clicked!')

        # Only allowed in client-side rendering.
        div(onClick=log_clicked)


For attribute names that are not valid Python identifiers or are reserved words in python, pass in a :py:class:`Mapping <collections.abc.Mapping>` as the first positional argument:

.. code-block:: python

    from blu.html import form, input, label

    form[
        label({'for': 'value-input'})['Value:'],
        input({'data-value': '23'}, id='value-input'),
    ]


.. code-block:: html

    <form>
        <label for="value-input">Value:</label>
        <input data-value="23" id="value-input"></input>
    </form>



Children
++++++++

You can add children to an html element using square bracket notation:

.. code-block:: python

    from blu.html import div, p

    div[
        p['Hi.'],
        p['Hello.']
    ]

.. code-block:: html

    <div>
        <p>Hi.</p>
        <p>Hello.</p>
    </div>

.. note::

    Using square bracket notation on an HTML element does not mutate the original; instead, it returns a copy with the new attributes.

    .. code-block:: python

        from blu.html import div

        without_children = div
        with_children = div['Hello, World!']

        without_children  # <div></div>
        with_children  # <div>Hello, World!</div>

.. note::

    When you set children on an HTML element, you completely replace any existing children, rather than appending to them:

    .. code-block:: python

        from blu.html import div

        original = div['A', 'B']
        
        original['C', 'D']  # <div>CD</div>


A child of an HTML element can be any of the following types:

- Another :class:`blu.HTMLElement`.
- A :py:class:`str`. In this case, it will be rendered as an HTML text node.
- :py:data:`None`. Nothing is rendered in the place where a :py:data:`None` value is found.
- A :py:class:`int`. This renders as a text node whose text is the :py:class:`str` representation of the integer.
- A :py:class:`float`. This renders as a text node whose text is the :py:class:`str` representation of the float.
- An :py:class:`Iterable <collections.abc.Iterable>` of valid children. This renders as all the child nodes contained in the :py:class:`Iterable <collections.abc.Iterable>`.

.. code-block:: python

    from blu.html import div, span, p

    div[
        span,
        'Hello!',
        None,
        1,
        1.0,
        (
            p,
            'Hello again!',
            None,
            2,
            2.0,
        )
    ]

.. code-block:: html

    <div>
        <span></span>
        Hello!11
        <p></p>
        Hello again!22
    </div>


.. note::

    Items in :py:class:`Iterable <collections.abc.Iterable>` children (other than :py:class:`str`\ s and :py:class:`tuple`\ s) must be keyed:

    .. code-block::

        from blu import Key
        from blu.html import div

        PEOPLE = [
            {'id': 0, 'name': 'Ana'},
            {'id': 1, 'name': 'Bill'},
            {'id': 2, 'name': 'Charlotte'},
        ]

        # Wrong!
        div[
            [f'Hello, {person["name"]}' for person in PEOPLE],
        ]

        # Right.
        div[
            [
                Key(person["id"])[
                    f'Hello, {person["name"]',
                ]
                for person in PEOPLE
            ],
        ]

        # Right.
        div[
            (
                'Hello, Ana!',
                'Hello, Bill!',
                'Hello, Charlotte!',
            ),
        ]

        # Right.
        div['Hello, Ana! Hello, Bill! Hello, Charlotte!']

    The rationale here is that, in :ref:`client-side rendering <Client-Side Rendering>`, items in a sequence may be moved around in response to user interaction. Giving keys to these items allows React to maintain state and render efficiently even when an item's position in a sequence changes.

You can tell Blu that items' positions won't change by putting them in a :py:class:`tuple`. If you do this, you won't have to key the items. For those familiar with React, this is how React `fragments <https://react.dev/reference/react/Fragment>`_ are defined in Blu.