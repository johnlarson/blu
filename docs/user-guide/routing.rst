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
        return p['This is an employee profile page.']

Now, if you go to ``/employees/325832``, or to ``/employees/839481``, or even to ``/employees/cheese``, you'll get something like this:

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

Notice that the *__page__()* function now has the argument *employee_id*. Because of this, Blu looks for a route segment in ``__index__.py``'s URL path that matches the argument name, with single underscores around it, and takes the value of that segment in the actual URL to pass in as that argument.

A route can have multiple dynamic segments::

    app/
      employees/
        _employee_id_/
          time_card/
            _date_/
              __index__.py

.. code-block:: python
    :caption: app/employees/_employee_id_/time_card/_date_/__index__.py

    from blu.html import p


    def __page__(employee_id, date):
        return p[f'This is employee #{employee_id}\'s time card for {date}.']


In this case, visiting ``/employees/325832/time_card/2024-12-10`` gives us:

    .. raw:: html

        <p>This is employee #325832's time card for 2024-12-10.</p>


Default Handlers
----------------

You can add a catch-all handler to a route segment that handles a request if the route is matched up to that point but no ``__index__.py`` file is on a path that exactly matches the URL. You do this by creating a ``__default__.py`` file with a *__page__()* function::

    app/
      foo/
        __default__.py
        bar/
          __index__.py

.. code-block:: python
    :caption: app/foo/__default__.py

    from blu.html import p


    def __page__():
        return p['This is the default page.']

.. code-block:: python
    :caption: app/foo/bar/__index__.py

    from blu.html import p


    def __page__():
        return p['This is the page for /foo/bar.']

In this example, visiting ``/foo/bar`` will give us:

    .. raw:: html

        <p>This is the page for /foo/bar.</p>

But visiting ``/foo`` or ``/foo/some/other/path`` or ``/foo/bar/some/other/path`` will give us:

    .. raw:: html

        <p>This is the default page.</p>

Accessing the remaining path
++++++++++++++++++++++++++++

To read the remaining, unmatched portion of the URL in a default handler, you can accept a positional-only argument in the *__page__()* function. This is done by adding a slash to *__page__()*'s function signature::

    app/
      foo/
        __default__.py

.. code-block:: python
    :caption: app/foo/__default__.py

    from blu.html import p


    def __page__(path, /):
        return p[f'The remaining path is {path}.']

In this example, visiting ``/foo/a/b/c`` gives us:

    .. raw:: html

        The remaining path is a/b/c.

Any dynamic route arguments should come after the slash::

    app/
      _my_param_/
        __default__.py


.. code-block:: python
    :caption: app/_my_param_/__default__.py

    from blu.html import b, p


    def __page__(path, /, my_param):
        return (
            p[
                b['my_param value:'], ' ', my_param,
            ],
            p[
                b['remaining path:'], ' ', path,
            ],
        )

In this example, visiting ``/my-param-value/a/b/c`` gives us:


    .. raw:: html

        <p>
            <b>my_param value:</b> my-param-value
        </p>
        <p>
            <b>remaining path:</b> a/b/c
        </p>


Query Parameters
----------------

To access a request's query parameters in an ``__index__.py`` or ``__default__.py`` handler, add keyword-only arguments to the *__page__()* function. This is done by adding an asterisk to the function signature::

    app/
      foo/
        __index__.py

.. code-block:: python
    :caption: app/foo/__index__.py

    from blu.html import b, p


    def __page__(*, bar, baz):
        return (
            p[
                b['bar:'], ' ', bar,
            ],
            p[
                b['baz:'], ' ', baz,
            ],
        )

In this example, visiting ``/foo?bar=A&baz=B`` gives us:

    .. raw:: html

        <p>
            <b>bar:</b> A
        </p>
        <p>
            <b>baz:</b> B
        </p>

The *__page__()* function can also accept a keyword argument :py:class:`dict`::

    app/
      foo/
        __index__.py

.. code-block:: python
    :caption: app/foo/__index__.py

    from blu.html import b, p


    def __page__(*, bar, **kwargs):
        return (
            p[
                b['bar:'], ' ', bar,
            ],
            p[
                b['baz:'], ' ', kwargs['baz'],
            ],
            p[
                b['hello:'], ' ', kwargs['hello']
            ],
        )

In this example, visiting ``/foo?bar=A&baz=B&hello=C`` gives us:

    .. raw:: html

        <p>
            <b>bar:</b> A
        </p>
        <p>
            <b>baz:</b> B
        </p>
        <p>
            <b>hello:</b> C
        </p>

If there are dynamic route arguments, those should come before the asterisk::

    app/
      _foo_/
        __index__.py
    
.. code-block:: python
    :caption: app/_foo_/__index__.py

    from blu.html import b, p


    def __page__(foo, *, bar, baz):
        return (
            p[
                b['foo:'], ' ', foo,
            ],
            p[
                b['bar:'], ' ', bar,
            ],
            p[
                b['baz:'], ' ', baz,
            ],
        )

In this example, visiting ``/A?bar=B&baz=C`` gives us:

    .. raw:: html

        <p>
            <b>foo:</b> A
        </p>
        <p>
            <b>bar:</b> B
        </p>
        <p>
            <b>baz:</b> C
        </p>


Return Values
-------------

A *__page__()* function can return any valid child of an HTML element (see the :ref:`Children` subsection of :ref:`Creating Pages`). The same rules apply for :py:class:`Iterable <collections.abc.Iterable>`\ s (again, see the :ref:`Children` subsection of :ref:`Creating Pages`):

.. code-block:: python

    from blu import Key
    from blu.html import p


    # Wrong! All Iterables except strings and tuples must be keyed.
    def __page__():
        return p[
            ['A', 'B', 'C'],
        ]
    
    # Right. The list is keyed.
    def __page__():
        return p[
            [
                Key(0)['A'],
                Key(1)['B'],
                Key(2)['C'],
            ],
        ]

    # Right. Strings don't have to be keyed, even though they are iterable.
    def __page__():
        return p['ABC']
    
    # Right. Tuples don't have to be keyed, even though they are iterable.
    def __page__():
        return p[
            ('A', 'B', 'C'),
        ]

You can also return a :class:`blu.Response` to set the status code and/or response headers of the page:

.. code-block:: python
    
    from blu import Response
    from blu.html import p


    def __page__():
        return Response(
            p['Hello.'],
            status=404,
            headers={
                'Cache-Control': 'no-cache',
                'Last-Modified': 'Tue, 10 Dec 2024 10:00:00 GMT',
            },
        )
