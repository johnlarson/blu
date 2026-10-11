``js`` (client-only)
====================

The JavaScript global scope is available in the client-side Python environment through the ``js`` module:

.. code-block:: python

    from blu import is_client

    __client__ = True


    if is_client:
        from js import Promise, addEventListener, alert, document


.. note::

    ``js`` can only be imported in a client context.

    .. code-block:: python

        from blu import is_client

        # Wrong!
        from js import document

        # Right.
        if is_client:
            from js import document


By default, Blu runs Python on the client using the MicroPython interpreter. You can view MicroPython's documentation on `in-browser type conversions <https://github.com/micropython/micropython/blob/master/ports/webassembly/README.md#proxying>`_ to learn how JavaScript types are converted into Python.

If you :doc:`opt in to using Pyodide </appendices/choosing-an-interpreter>` as your client-side Python interpreter, you can learn about Pyodide's type conversions `here <https://pyodide.org/en/stable/usage/type-conversions.html>`_.