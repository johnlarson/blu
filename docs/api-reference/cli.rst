Command Line Interface
======================

.. todo::

  Document the following:

  dev
  build

.. code-block:: console
   
  $ blu [command]

When you install Blu, the Blu command line interface (CLI) will also be installed and made available in your system path as ``blu``.

Before running it, ``cd`` into your project root (the directory containing the ``app/`` directory).

Blu's CLI exposes the following commands:


``dev``
-------

.. code-block:: console

  $ blu dev

Run the development server.

The development server automatically builds your app and runs it, rebuilding and restarting any time a change is made to your app directory.

The deveopment server will automatically find an available port to run on, and once it has started, the ``blu dev`` process will give you output like the following, showing the URL where your app is running:

.. todo:: Get the output for this.