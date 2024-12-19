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

You can import any HTML tag from :mod:`blu.html`, as long as the tag name is a valid Python identifier:

.. code-block:: python

    from blu.html import div, span, select, canvas, mymadeuptagname


    def __page__():
        return html[
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


Children
++++++++

You can add children to an html element using square bracket notation:

.. code-block:: python

    from blu.html import div, span, br


    div[
        p['Hi.'],
        p['Hello.']
    ]

.. code-block:: html

    <div>
        <p>Hi.</p>
        <p>Hello.</p>
    </div>