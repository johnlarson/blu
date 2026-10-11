.. _pyscript:

``pyodide`` (opt-in)
====================

By default, Blu uses MicroPython as its client-side Python interpreter. However, you can also :doc:`opt in to using Pyodide </appendices/choosing-an-interpreter>` as your Python interpreter.

Pyodide provides an additional client-side package called ``pyodide``, which provides utilities for using Python in the browser.

.. code-block:: python

    from blu import is_client

    if is_client:
        from pyodide.http import pyfetch
    
    response = await pyfetch('https://www.example.com/api/v2/data')
    print(await response.json())

.. note::

    The ``pyodide`` package can only be imported in a client context.

    .. code-block:: python

        from blu import is_client

        # Wrong!
        from pyodide.http import pyfetch

        # Right.
        if is_client:
            from pyodide.http import pyfetch


For more information on the ``pyodide`` package, see the package's official `API reference <https://pyodide.org/en/stable/usage/api/python-api.html>`_.