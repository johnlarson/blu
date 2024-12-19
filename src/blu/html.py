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

from blu._react.types import HTMLElement as _HTMLElement


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

    :param import_name: An HTML tag name.

    :return: A :class:`blu.HTMLElement` whose tag name is **import_name**.
    """
    ...