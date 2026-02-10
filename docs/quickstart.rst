Quickstart
==========

If you haven't already, :ref:`install Blu <install>`.

Next, create a directory called ``app``. Inside this directory, create a file called ``__index__.py`` with the following content:

.. code-block:: python
  :caption: app/__index__.py

  from blu.html import body, head, html

  def __page__():
      return html[
          head,
          body['Hello World!'],
      ]

Your project should look like this::

  app/
    __index__.py


To start up a development instance of your app, enter the following in a terminal (make sure you are in the parent directory of ``app/``, not in the ``app/`` directory itself):

.. code-block:: console
   
   $ blu

This will start up the app and output a url where you can access it (``http://127.0.0.1:{some port}``). Visit this url in a web browser, and you should see the following:

  .. raw:: html
   
     <html>
       <head></head>
       <body>Hello World!</body>
     </html>

If it works, you've created a simple web app using Blu.

To learn how make more complex pages in Blu, see :ref:`Creating Pages`.