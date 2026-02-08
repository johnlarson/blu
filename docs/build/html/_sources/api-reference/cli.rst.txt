Command Line Interface
======================

.. code-block:: console
   
  $ blu [command]

When you install Blu, the Blu command line interface (CLI) will also be installed and made available in your system path as ``blu``.

Before running it, ``cd`` into your project root (the directory containing the ``app/`` directory).

Blu's CLI exposes the following commands:


``build``
---------

.. code-block:: console
  
  $ blu build

Build your app (this is a required step before deploying).

Generates static files in the ``static/`` directory. These can be copied to a static files directory or uploaded into a CDN. Blu also uses this directory internally, so make sure you don't delete it after copying.

One of the things Blu does internally with this directory is to serve static files. So if you don't have a static server or CDN, your Blu app will still be able to run. However, this is not the only internal use of the static files, so even if you have an external static server, don't delete ``static/``.

``blu build`` also creates a ``.build/`` directory. You shouldn't need to work with the directory yourself; just know that it shouldn't be deleted, because Blu uses it internally. If it is deleted, it can be re-created by running ``blu build`` again.


``dev``
-------

.. code-block:: console

  $ blu dev

Run the development server.

The development server automatically builds your app and runs it, rebuilding and restarting any time a change is made to your app directory.

The deveopment server will automatically find an available port to run on, and once it has started, the ``blu dev`` process will give you output like the following, showing the URL where your app is running:

.. todo:: Get the output for this.


