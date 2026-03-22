Command Line Interface
======================

.. code-block:: console
   
  $ blu

When you install Blu, the Blu command line interface (CLI) will also be installed and made available in your system path as ``blu``.

Run ``blu`` from your project root (the directory containing the ``app/`` directory) to start a development server that runs your app and restarts any time a change is made to Python files in your app directory.

The deveopment server will automatically find an available port to run on, and once it has started, the ``blu`` process will give you output like the following, showing the URL where your app is running:

.. code-block:: none

  INFO:     Uvicorn running on http://127.0.0.1:50227 (Press CTRL+C to quit)

Don't run the development server in production. See :ref:`Deploying Your App` for details on how to deploy an app to a production environment.
