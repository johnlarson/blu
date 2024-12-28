.. _routing:

Routing
=======

The :ref:`Quickstart` guide shows how to serve a page from ``/`` using Blu.

This section explains how to serve pages from other paths.


File-Based Routing
------------------

Blu uses file-based routing. This means that the path that a page is served from is based on the file's location in the ``app/``.

For example, if you want to serve the page in the :ref:`Quickstart` guide from ``/path/to/page`` instead of from ``/``, you would move the ``__index__.py`` file from ``app/`` to ``app/path/to/page``:

.. code-block:: python
    :caption: app/path/to/page/__index__.py

    from blu.html import body, head, html

    def __page__():
        return html[
            head,
            body['Hello World!'],
        ]

After this change, your project directory would look like this::

    app/
      path/
        to/
          page/
            __index__.py


Dynamic Route Segments
----------------------

To add a dynamic route segment, create a directory whose name is surrounded by single underscores, like the ``_employee_id_`` directory in this example::

    app/
      employees/
        _employee_id_/
          __index__.py

.. code-block:: python
    :caption: app/employees/_employee_id_/__index__.py

    from blu.html import p

    def __page__():
        p[f'This is an employee profile page.']

Now, if you go to ``/employees/325832``, or to ``/employees/839481``, or event to ``/employees/cheese``, you'll get something like this:

.. raw:: html

    <p>This is an employee profile page.</p>

Dynamic route segments usually aren't that useful unless there's actual dyanmic content, so let's use that employee id from the URL path in our page:

.. code-block:: python
    :caption: app/employees/_employee_id_/__index__.py

    from blu.html import p

    def __page__(employee_id):
        return p[f'This is the profile page for employee #{employee_id}.']

Now, visiting ``/employees/325832`` gives us:

.. raw:: html

    <p>This is the profile page for employee #325832.</p>

Notice that the *__page__* function now has the argument *employee_id*. Because of this, Blu looks for a route segment in ``__index__.py``'s URL path that matches the argument name, with single underscores around it, and takes the value of that segment in the actual URL to pass in as that argument.

A route can have multiple dynamic segments::

    app/
      employees/
        _employee_id_/
          time_punch/
            _date_/
              __index__.py

.. code-block:: python
    :caption: app/employees/_employee_id_/time_punch/_date_/__index__.py

    def __page__(employee_id, date):
        return p[f'This is employee #{employee_id}\'s time card for {date}.']


In this case, visiting ``/employees/325832/time_card/2024-12-10`` gives us:

.. raw:: html

    <p>This is employee #325832's time card for 2024-12-10.</p>



              