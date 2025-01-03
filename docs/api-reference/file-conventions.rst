File Conventions
================

.. todo::

    Intro

    Document the following:

    - __index__.py - explain
        - __page__()
    - __default__ - explain
        - __page__()




Segments
--------

``{literal_segment}``
+++++++++++++++++++++

A static route segment.

.. code-block:: python
    :caption: app/hello/__index__.py

    from blu.html import p


    def __page__():
        return p['Hello, World!']

**/hello**

    .. raw:: html

        <p>Hello, World!</p>

**Capture** *literal_segment* - A string that doesn't start or end with an underscore.

**Matches** - A path segment that equals *literal_segment*.

``_{route_param_name}_``
++++++++++++++++++++++++

A dynamic route segment.

.. code-block:: python
    :caption: app/_slug_/__index__.py

    from blu.html import p

    
    def __page__(slug):
        return p['The slug value is: ', slug]
    
**/some-slug-value**

    .. raw:: html

        <p>The slug value is: some-slug-value</p>

**Capture** *route_param_name* - A valid Python identifier that doesn't start or end with an underscore.

**Matches** - Any path segment.

*route_param_name* is passed down to the handler under this segment that matches the URL path, if any.

Files
-----

__index__.py
++++++++++++

Handle a request whose URL matches the path to this file from the ``app/`` directory.

.. code-block:: python
    :caption: app/static_segment/_slug_/__index__.py

    from blu.html import p

    
    def __page__(slug, *, q):
        return (
            p['The slug value is: ', slug],
            p['The query param value is: ', q],
        )

**/static_segment/some-slug-value?q=some-query-value**

    .. raw:: html

        <p>The slug value is: some-slug-value</p>
        <p>The query param value is: some-query-value</p>

An __index__.py file should define the following top-level call signature:

.. py:function:: __page__([path: str, /,] ***url: str) -> blu.Node | blu.Response | flask.Response


**Location** - Under a segment directory.

**Matches** - A URL path that matches every segment in the path from the app directory to this file, and has no extra, unmatched URL path segments.


__default__.py
++++++++++++++

Handle a request whose URL matches a prefix of the path to this file from the ``app/`` directory, if no match is found at a lower level.

.. code-block:: python
    :caption: app/static_segment/_slug_/__default__.py

    from blu.html import p

    
    def __page__(path, /, slug, *, q):
        return (
            p['The remaining path is: ', path],
            p['The slug value is: ', slug],
            p['The query param value is: ', q],
        )

**/static_segment/some-slug-value/some/extra/path?q=some-query-value**

    .. raw:: html

        <p>The remaining path is: some/extra/path</p>
        <p>The slug value is: some-slug-value</p>
        <p>The query param value is: some-query-value</p>


**Location** - Under a segment directory.

**Matches** - A URL path that matches every segment in the path from the app directory to this file, but which has no matching handler in or below the directory containing the __default__.py file.


__settings__.py
+++++++++++++++

Configure your Blu app.

.. code-block:: python
    :caption: app/__settings__.py

    CLIENT_REQUIREMENTS = ['arrr', 'aiohttp']

**Location** - The root of the ``app/`` directory, i.e. the app directory should be the immediate parent directory of __settings__.py.

**Matches** - n/a (doesn't handle requests).

You can configure your Blu app by creating a __settings__.py file and assigning configuration values at the top level of the file. For example, the __settings__.py file at the beginning of this section sets the *CLIENT_REQUIREMENTS* configuration property to ``['arrr', 'aiohttp']``.

A __settings__.py file is not required, and an app without a __settings__.py file will be treated the same as an app whose __settings__.py is empty.

A __settings__.py file can have any of settings defined in the :class:`blu.Settings` protocol.


.. _file-conventions/files/what-does-triple-start-url-mean:

How to read function signatures in this section
+++++++++++++++++++++++++++++++++++++++++++++++

Blu defines protocols for request handler functions. These protocols outline what functions *you* can define, rather than what functions Blu has defined for you. This makes the protocol more flexible, so we use slightly different conventions that usual to document them.

\*\*\*url
^^^^^^^^^

Triple asterisks denote arguments captured from the URL.

.. todo:: Explain...

Square brackets
^^^^^^^^^^^^^^^

Square brackets denote arguments that don't have to be in the function call signature, but can. For example, the __default__.py *__page__()* function's arguments can optionally start with a positional-only argument of type string, followed by a slash:

.. py:function:: __page__([path: str, /,] ***url) -> blu.Node | blu.Response | flask.Response

.. code-block:: python

    # Right.
    def __page__(route_param_1, route_param_2):
        ...

    # Right.
    def __page__(path, /, route_param_1, route_param_2):
        ...

    # Right.
    def __page__(path_with_different_arg_name, /, route_param_1, route_param_2):
        ...

    # Wrong!
    def __page__(/, route_param_1, route_param_2):
        ...

    # Probably wrong (forgot the slash before path). But if you meant to include a route param called "path", you're doing it right.
    def __page__(path, route_param_1, route_param_2):
        ...

    # Right.
    def __page__():
        ...
    
    # Right.
    def __page__(path, /):
        ...

    # Wrong!
    def __page__(/)

You can include type annotations in your function definition, but don't have to; the type annotations in the documentation just tell you what type Blu will pass in for each argument.

.. code-block:: python

    # Right.
    def __page__(path, /):
        ...

    # Also right!
    def __page__(path: str, /):
        ...

Return types
^^^^^^^^^^^^

The return type tells you what return type Blu is expecting.

For example, the *__page__()* function in __index__.py has to return a :type:`blu.Node`, a :class:`blu.Response`, or a :class:`quart.Response`:

.. py:function:: __page__(***url) -> blu.Node | blu.Response | flask.Response


.. code-block:: python

    from blu import Response
    from blu.html import p
    import quart

    # Right.
    def __page__():
        return p['Hello World!']
    
    # Right.
    def __page__():
        return Response(p['Page not found.'], status=404)
    
    # Right.
    def __page__():
        return quart.make_response({'hello': 'world'})

    # Wrong!
    def __page__():
        return {'hello': 'world'}

You don't have to annotate the return type, but you can. Any return type that is a subset of that shown in the documentation is valid.

.. code-block:: python

    import blu
    import quart


    # Right.
    def __page__():
        ...

    # Also right.
    def __page__() -> blu.Node | blu.Response | quart.Response:
        ...

    # Also right!
    def __page__() -> blu.Node:
        ...

    # Wrong!
    def __page__() -> dict:
        ...

    # Right; strings are blu.Nodes.
    def __page__() -> str:
        ...


Static Files
------------

Any non-Python file under the ``app/`` directory will be treated as a static file and will be served from the path it is at relative to the ``app/`` directory.

For example, if you have a text file at ``app/path/to/file.txt``, you will be able to download that file from ``/path/to/file.txt``.

.. note::

    Static files are served statically even if they are under a dynamic route. So if you have a file at ``app/_id_/file.txt``, then sending a request to ``/some-id/file.txt`` will result in an HTTP 404 error. Instead, you would access the file at ``/_id_/file.txt``.

Blu serves static files in production as well as in development, but if you want to serve static files from a separate service, you can access them in the ``static/`` directory (this will be in your project root, in the same parent directory as ``app/``) after :ref:`building your app <Building Your App>`.


