External Packages
=================

.. todo::

    Document the following:
    
    - js


Blu operates in a `Quart <https://quart.palletsprojects.com>`_ request context on the back end and a PyScript environment on the front end. As a result, some packages external to Blu are available to you without you having to install them. This document lists them and explains how they operate in a Blu app.


Available on the Server
-----------------------

``quart``
+++++++++

`Quart <https://quart.palletsprojects.com>`_ is a Python web framework. It's basically an asynchronous version of Flask, made by the developers of Flask. So if you've used Flask before, Quart will be familiar.

Blu request handlers are run in a Quart request context, so you can access request information the same way you can in a Quart app:

.. code-block:: python

    from blu.html import p
    from quart import request

    async def __page__():
        header_value = request.headers['X-Hello']
        return p['Got value ', header_value, ' for header X-Hello']
    
Additionally, Blu request handlers can return Quart responses. The following example uses Quart request and response objects to create a REST API endpoint.

.. code-block:: python

    from quart import request, make_response

    from app.some_business_logic_module import create_item

    async def __page__():
        if request.method != 'POST':
            response = make_response({'message': f'Expected a POST request; received a {request.method} request.')
            response.status = 405
            return response
        new_item = await request.get_json()
        new_item_id = await create_item(new_item)
        return make_response({
            **new_item,
            'id': new_item_id,
        })

For more information, see:

- `This cheatsheet for the Quart request object <https://quart.palletsprojects.com/en/latest/reference/cheatsheet.html#request>`_
- `API reference for the Quart request object <https://quart.palletsprojects.com/en/latest/reference/source/quart.wrappers.html#quart.wrappers.Request>`_
- `The API reference for Quart Response objects <https://quart.palletsprojects.com/en/latest/reference/source/quart.wrappers.response.html#quart.wrappers.response.Response>`_
- `Quart's official site <https://quart.palletsprojects.com>`_


Available on the Client
-----------------------


.. _external-packages/pyscript:

``pyscript``
++++++++++++

PyScript is an tool created by Anaconda that runs Python in web browsers. Client-side code in a Blu app is run in a PyScript environment. Because of this, the ``pyscript`` package is available to your client-side code.

The ``pyscript`` package provides Python utilities for working within a browser environment.

.. code-block:: python

    from blu import client

    
    def handle_click(e):
        print('Clicked!')
    

    if client:
        from pyscript import window

        window.addEventListener('click', handle_click)

.. note::

    ``pyscript`` can only be imported in a client context.

    .. code-block:: python

        from blu import client

        # Wrong!
        from pyscript import window

        # Right.
        if client:
            from pyscript import window


.. note::

    Blu configures PyScript to use MicroPython.
    
    PyScript gives the option of a more feature-complete but less-efficient Python interpreter called Pyodide, or a faster interpreter called MicroPython.

    Because Blu uses MicroPython, not all Python standard library modules are available client-side, and many PyPI packages are not compatible with Blu's client-side environment.

    For more information, see https://docs.pyscript.net/2024.11.1/user-guide/architecture/#interpreters.

For more information on the ``pyscript`` package, see the package's official `API reference page <https://docs.pyscript.net/2024.11.1/api/>`_.

``js``
++++++

Because Blu's client-side code :ref:`runs in a PyScript environment <external-packages/pyscript>`, the ``js`` module is also available client-side.