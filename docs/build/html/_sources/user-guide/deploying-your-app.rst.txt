Deploying Your App
==================

Blu is an ASGI framework, meaning it doesn't include tools for running a production server. Instead, it exposes an ASGI app that can be run by an ASGI server.

If you're familiar with ASGI frameworks, you may be wondering, "Where is the ASGI app?" The app you'll use to deploy is :data:`blu.app`.

For example, to deploy your app using `Uvicorn <uvicorn.org>`_, run the following from your ``app/`` directory's parent directory (not the ``app/`` directory itself):

.. code-block:: console
   
   $ uvicorn blu:app

.. note::
   
   You'll have to make sure your ``app/`` directory is in your Python path, as :data:`blu.app` will expect an ``app`` module that it can import your app definition from. For most ASGI implementations, this can be acheived by running the ASGI server from the ``app/`` directory's parent directory as in the previous example using Uvicorn.


