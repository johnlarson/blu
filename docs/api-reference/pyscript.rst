``pyscript`` (client-only)
==========================

PyScript is an tool created by Anaconda that runs Python in web browsers. Client-side code in a Blu app is run in a PyScript environment. Because of this, the ``pyscript`` package is available to your client-side code.

The ``pyscript`` package provides Python utilities for working within a browser environment.

.. code-block:: python

    from blu import is_client

    
    def handle_click(e):
        print('Clicked!')
    

    if is_client:
        from pyscript import window

        window.addEventListener('click', handle_click)

.. note::

    ``pyscript`` can only be imported in a client context.

    .. code-block:: python

        from blu import is_client

        # Wrong!
        from pyscript import window

        # Right.
        if is_client:
            from pyscript import window


.. note::

    Blu configures PyScript to use MicroPython.
    
    PyScript gives the option of a more feature-complete but less-efficient Python interpreter called Pyodide, or a faster interpreter called MicroPython.

    Because Blu uses MicroPython, not all Python standard library modules are available client-side, and many PyPI packages are not compatible with Blu's client-side environment.

    For more information, see https://docs.pyscript.net/2024.11.1/user-guide/architecture/#interpreters.

For more information on the ``pyscript`` package, see the package's official `API reference page <https://docs.pyscript.net/2024.11.1/api/>`_.