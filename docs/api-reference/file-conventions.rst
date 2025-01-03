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

What does *\*\*\*url* mean?
+++++++++++++++++++++++++++

Route handlers in Blu allow you to capture route parameters from dynamic path segments and query parameters from the query string by adding keyword-only and positional/keyword arguments to the function (positional-only arguments don't capture route or query parameters).

In this document, ``***url`` at the end of a function signature acts as a placeholder for positional/keyword and keyword-only arguments, and indicates that these arguments can capture route and query parameters as follows:

Capturing route parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^

You can capture route parameters from dynamic route segments using positional/keyword arguments:

.. code-block:: python
    :caption: app/employees/_employee_id_/time_punch/_date_/__index__.py

    from blu.html import p


    def __page__(employee_id, date):
        return p[
            'Time punch info for employee #',
            employee_id,
            ' on ',
            date,
        ]

.. code-block:: html
    :caption: GET /employees/2345820390/time_punch/2024-12-01

    <p>Time punch info for employee #2345820390 on 2024-12-01</p>

Capturing query parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^

You can capture query parameters using keyword-only arguments:

.. code-block:: python
    :caption: app/greet-me/__index__.py

    from blu.html import p


    def __page__(*, my_name):
        return p['Hello ', my_name, '!']

.. code-block:: html
    :caption: GET /greet-me?my_name=Kevin

    <p>Hello Kevin!</p>

You can set default values for query parameters:

.. code-block:: python
    :caption: app/greet-me/__index__.py

    from blu.html import p


    def __page__(*, my_name='World'):
        return p['Hello ', my_name, '!']

.. code-block:: html
    :caption: GET /greet-me?my_name=Kevin

    <p>Hello World!</p>

You can also use ``**kwargs`` for query parameters:

.. code-block:: python
    :caption: app/greet-me/__index__.py

    from blu.html import p


    def __page__(*, my_name, **kwargs):
        greeting = kwargs.get('greeting', 'Hello')
        return p[greeting, ' ', my_name, '!']

.. code-block:: html
    :caption: GET /greet-me?my_name=Kevin&greeting=Hi

    <p>Hi Kevin!</p>

Handler-specific arguments
^^^^^^^^^^^^^^^^^^^^^^^^^^

Positional-only arguments are reserved for handler-specific arguments.

For example, the *__page()__* function of __default__.py files allows you to get the remaining portion of the URL path using a positional-only argument (in Python, positional-only arguments are at the beginning of the argument list, separated from other arguments with a ``/``):

.. code-block:: python
    :caption: app/foo/__default__.py

    from blu.html import p

    def __page__(path, /):
        return p['Remaining path: ', path]

.. code-block:: html
    :caption: Get /foo/bar/baz

    <p>Remaining path: bar/baz</p>

Blu passes these arguments in by position, so unlike route- and query-parameter-capturing arguments, they can have any name:

.. code-block:: python
    :caption: app/foo/__default__.py

    from blu.html import p

    def __page__(remaining_path, /):
        return p['Remaining path: ', remaining_path]


Static Files
------------

Any non-Python file under the ``app/`` directory will be treated as a static file and will be served from the path it is at relative to the ``app/`` directory.

For example, if you have a text file at ``app/path/to/file.txt``, you will be able to download that file from ``/path/to/file.txt``.

.. note::

    Static files are served statically even if they are under a dynamic route. So if you have a file at ``app/_id_/file.txt``, then sending a request to ``/some-id/file.txt`` will result in an HTTP 404 error. Instead, you would access the file at ``/_id_/file.txt``.

Blu serves static files in production as well as in development, but if you want to serve static files from a separate service, you can access them in the ``static/`` directory (this will be in your project root, in the same parent directory as ``app/``) after :ref:`building your app <Building Your App>`.


