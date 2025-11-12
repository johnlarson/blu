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


If the HTML tag name you want to import is a reserved word in Python, add a trailing underscore to the import name:

.. code-block:: python

    from blu.html import del_

    del_['Hello, World!']

.. code-block:: html

    <del>Hello, World!</del>

All non-trailing underscores will be converted to dashes:

.. code-block:: python

    from blu.html import tag_name_with_dashes

    tag_name_with_dashes['Hello!']

.. code-block:: html

    <tag-name-with-dashes>Hello!</tag-name-with-dashes>

In the rare case your desired tagname cannot be imported from the :mod:`blu.html` module, use :func:`blu.create_rare_html_element`. 


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


To include an attribute name that is a reserved word in Python, add a trailing underscore:


.. code-block:: python

    from html import form, input, label

    form[
        label(for_='email-address-input')['Name:'],
        input(id='email-address-input'),
    ]


.. code-block:: html

    <form>
        <label for="email-address-input">Value:</label>
        <input id="email-address-input"></input>
    </form>


All non-trailing underscores will be converted to dashes:


.. code-block:: python

    from html import input

    input(data_value=23)


.. code-block:: html

    <input data-value="23"></input>


You can also directly set an attribute name by passing a :py:class:`Mapping <collections.abc.Mapping>` as the first positional argument:


.. code-block:: python

    from html import div

    div({'attr_1_': 'value 1'}, attr_2_='value 2')


.. code-block:: html

    <div attr_1_="value 1" attr-2="value 2"></div>



Children
++++++++

.. include:: /_includes/client-element-children.rst

You can tell Blu that items' positions won't change by putting them in a :py:class:`tuple`. If you do this, you won't have to key the items. For those familiar with React, this is how React `fragments <https://react.dev/reference/react/Fragment>`_ are defined in Blu.