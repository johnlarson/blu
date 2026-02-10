``js`` (client-only)
====================

Because Blu's client-side code :ref:`runs in a PyScript environment <external-packages/pyscript>`, the ``js`` module is also available client-side.

This module allows access to the JavaScript environment's global namespace:

.. code-block:: python

    from blu import is_client


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


The ``js`` module allows you to work with native JavaScript web APIs within your client-side code.

PyScript provides the choice of two Python interpreters: Pyodide and MicroPython. Blu uses Pyodide. You can view the `Type translations <https://pyodide.org/en/stable/usage/type-conversions.html>`_ section in Pyodide's documentation to learn more about how JavaScript objects are converted when imported into a Python scope.