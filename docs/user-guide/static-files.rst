Static Files
============

To serve a static file, place it in your ``app/`` directory in the route that it should be served from::

  app/
    path/
      to/
        static/
          file.txt


.. code-block::
    :caption: app/path/to/static/file.txt

    Hello, World!

Now, visiting ``/path/to/static/file.txt`` will give us a response whose body is ``Hello, World!``.

.. note::
   
   When a static file is placed under a :ref:`dynamic route segment <Dynamic Route Segments>`, it is still served from a static path. So for example, a file at
   
   ``app/static_segment/_dynamic_segment_/my_file.txt``
   
   can only be accessed at the URL path
   
   ``/static_segment/_dynamic_segment_/my_file.txt``
   
   not at
   
   ``/static_segment/some-dynamic-segment-value/my_file.txt``