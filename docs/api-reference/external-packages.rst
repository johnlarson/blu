External Packages
=================

.. todo::

    Document the following:

    - quart
    - js
    - pyscript


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

- `Quart's official site <https://quart.palletsprojects.com>`_
- `This cheatsheet for the Quart request object <https://quart.palletsprojects.com/en/latest/reference/cheatsheet.html#request>`_
- `API reference for the Quart request object <https://quart.palletsprojects.com/en/latest/reference/source/quart.wrappers.html#quart.wrappers.Request>`_




Available on the Client
-----------------------


``pyscript``
++++++++++++

(What it is and why you use it in Blu)


How it works in Blu
^^^^^^^^^^^^^^^^^^^


Documentation links
^^^^^^^^^^^^^^^^^^^


``js``
++++++

(What it is and why you use it in Blu)

How it works in Blu
^^^^^^^^^^^^^^^^^^^


Documentation links
^^^^^^^^^^^^^^^^^^^