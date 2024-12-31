Deploying Your App
==================

Deploying your app is a two-step process:

1. Build your app.

2. Start up an ASGI server for your app.

Building Your App
-----------------

To build your app, ``cd`` into your ``app/`` directory's parent directory (not the ``app/`` directory itself) and run:

.. code-block:: console
   
   $ blu build

This will create two directories at the same level as your app directory:

1. ``.build/`` - A hidden directory with private files needed by your app to run correctly in production. You don't need to edit or view any files in this directory.

.. note::
   Make sure not to delete the ``.build`` directory, as it is needed by your app in order to run correctly.

2. ``static/`` - This is where your static files are. Blu serves static files in production as well as in dev, but you'll likely want to use a different service to serve static files (for example, using Nginx's ``try_files`` directive). For those use cases, this is where you can find your static files.

.. note::
   
   If you don't have a separate static file server set up, make sure not to remove this directory, as Blu will look here for static files.

After a build, your project root (the directory containing your ``app/`` directory) should look like this::

  app/
    ... (your app files)
  static/
    ... (static files used in client-side code)
  .build/
    ... (private files required by your app to run correctly)


Starting Up the ASGI Server
---------------------------

If you're familiar with ASGI frameworks, you may be wondering, "Where is the ASGI app?" The app you'll use to deploy is :data:`blu.app`.

For example, to deploy your app using `Uvicorn <uvicorn.org>`_, run the following from your ``app/`` directory's parent directory (not the ``app/`` directory itself):

.. code-block:: console
   
   $ uvicorn blu:app

.. note::
   
   You'll have to make sure your ``app/`` directory is in your Python path, as :data:`blu.app` will expect an ``app`` module that it can import your app description from. For most ASGI implementations, this can be acheived by running the ASGI server from the ``app/`` directory's parent directory as in the previous example using Uvicorn.


