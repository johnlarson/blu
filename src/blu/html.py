"""
React HTML elements.

.. code-block:: python

    from blu.html import div, p

    div(className='my-div')[
        p['Hello!'],
        p['Hi.'],
    ]

.. code-block:: html

    <div className='my-div'>
        <p>Hello!</p>
        <p>Hi.</p>
    </div>
"""

from blu._nodes import HTMLElement as _HTMLElement


def __getattr__(import_name: str) -> _HTMLElement:
    """
    Creates a :class:`blu.HTMLElement` with the given
    HTML tag name.

    .. code-block:: python

        from blu.html import div, p

        div(className='my-div')[
            p['Hello!'],
            p['Hi.'],
        ]

    .. code-block:: html

        <div className='my-div'>
            <p>Hello!</p>
            <p>Hi.</p>
        </div>


    Use a trailing underscore to import tag names that are reserved
    words in Python (the trailing underscore won't show up in the
    resulting html):

    .. code-block:: python

        from blu.html import del_

        del_['Hello, World!']

    .. code-block:: html

        <del>Hello, World!</del>

    Non-trailing underscores will be converted to dashes:

    .. code-block:: python

        from blu.html import my_custom_element

        my_custom_element['Hello!']

    .. code-block:: html

        <my-custom-element>Hello!</my-custom-element>

    For the rare case where your desired HTML tag name cannot be
    imported from :mod:`blu.html`, use
    :func:`blu.create_rare_html_element`.

    :param import_name: An HTML tag name.

    :return: A :class:`blu.HTMLElement` whose tag name is
        ``import_name`` with the last trailing underscore (if any)
        removed and any other underscores converted to dashes. The
        :class:`HTMLElement <blu.HTMLElement>` won't have any props or
        children.
    """
    from blu._nodes import py_to_html_name

    if import_name == "__mro__":
        raise AttributeError(
            "module 'blu.html' has no attribute '__mro'",
        )

    return _HTMLElement(py_to_html_name(import_name), {}, [])
