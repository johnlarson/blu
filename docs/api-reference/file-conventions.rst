File Conventions
================

A Blu app is defined by the :ref:`special files <Special Files>` under its ``app/`` directory. The ``app/`` directory should be placed in the project root (this is where you run ``blu dev`` from).

Note that some special files' behavior is influenced by :ref:`the directories in their paths <Directories>`, relative to the ``app/`` directory.

You can also put :ref:`static files <Static Files>` in the ``app/`` directory.


Directories
-----------

Any directory placed under the ``app/`` directory is used for file-based routing. Each directory represents one of the slash-separated segments in an HTTP request's URL path (see examples for each directory type).

The behavior of certain special files like __index__.py is influenced by the paths of the segment directories they are under.

Each directory type follows a specified pattern for directory name and has set behavior.

**{**\ *literal_segment*\ **}**
+++++++++++++++++++++++++++++++

``^(?P<literal_segment>(?!_).\*[^_])$``

(no leading or trailing underscores; *literal_segment* is the directory name)

A static route segment. Matches a URL path segment that equals *literal_segment*.

.. code-block:: python
    :caption: app/hello/__index__.py

    from blu.html import p


    def __page__():
        return p['Hello, World!']

.. code-block:: html
    :caption: GET /hello

    <p>Hello, World!</p>

**_{**\ *route_param_name*\ **}_**
++++++++++++++++++++++++++++++++++

``^_(?P<route_param_name>[^\\W\\d_]|[^\\W\\d_][\\w]*[^\\W_])_$``

(*route_param_name*, surrounded by single underscores, where *route_param_name* is a valid python identifier that doesn't start or end with an underscore)

A dynamic route segment. Matches any path segment.

*route_param_name* is passed down to the handler under this segment that matches the URL path, if any.

.. code-block:: python
    :caption: app/_slug_/__index__.py

    from blu.html import p

    
    def __page__(slug):
        return p['The slug value is: ', slug]

.. code-block:: html
    :caption: GET /some-slug-value

    <p>The slug value is: some-slug-value</p>

Special Files
-------------

These files specify the behavior of your app. Some handle routes based on the location of the special file; others go at the top-level of the ``app/`` directory and specify app-wide behavior.

__index__.py
++++++++++++

Handles a request whose full URL matches all directories in the path to this file from the ``app/`` directory.

::

    app/
      foo/
        bar/
          __index__.py
    
    # Matches
    /foo/bar

    # Doesn't match
    /
    /foo
    /foo/baz
    /foo/some/other/path

Top-level functions
^^^^^^^^^^^^^^^^^^^

.. py:function:: __page__(***url) -> blu.Node | blu.Response | flask.Response

    Handle a request whose URL path is matched by this file.

    .. code-block:: python
        :caption: app/static_segment/_slug_/__index__.py

        from blu.html import p

        
        def __page__(slug, *, q):
            return (
                p['The slug value is: ', slug],
                p['The query param value is: ', q],
            )

    .. code-block:: html
        :caption: GET /static_segment/some-slug-value?q=some-query-value

        <p>The slug value is: some-slug-value</p>
        <p>The query param value is: some-query-value</p>

    :param url: (see :ref:`file-conventions/files/what-does-triple-start-url-mean`)
    
    :return: - If an instance of :type:`blu.Node`, the page that should be sent in the HTTP response.

        - If an instance of :type:`blu.Node` or :type:`quart.Node`, the HTTP response that should be sent.


__default__.py
++++++++++++++

Handles a request for which the directories in the path to this file from the ``app/`` directory match a prefix of the URL path, if no other handler file at or below this level matches the URL.

::

    app/
        foo/
          __default__.py
          bar/
            __index__.py

    
    # Matches
    /foo
    /foo/baz
    /foo/some/other/path

    # Doesn't match
    /foo/bar
    /
    /hello

Top-level functions
^^^^^^^^^^^^^^^^^^^


.. py:function:: __page__([path: str, /, ]***url) -> blu.Node | blu.Response | flask.Response

    Handle a request whose URL path is matched by this file.

    .. code-block:: python
        :caption: app/static_segment/_slug_/__default__.py

        from blu.html import p

        
        def __page__(path, /, slug, *, q):
            return (
                p['The remaining path is: ', path],
                p['The slug value is: ', slug],
                p['The query param value is: ', q],
            )

    .. code-block:: html
        :caption: GET /static_segment/some-slug-value/some/extra/path?q=some-query-value

        <p>The remaining path is: some/extra/path</p>
        <p>The slug value is: some-slug-value</p>
        <p>The query param value is: some-query-value</p>

    :param path: The remaining, unmatched portion of the URL, with no intial or trailing ``/``.
    :param url: (see :ref:`file-conventions/files/what-does-triple-start-url-mean`)

    :return: - If an instance of :type:`blu.Node`, the page that should be sent in the HTTP response.

        - If an instance of :type:`blu.Node` or :type:`quart.Node`, the HTTP response that should be sent.
    
    Note that the *path* argument is not required, so the following is valid:

    .. code-block:: python

        def __page__(some_route_param):
            ...

    Also note that Blu recognizes the *path* parameter regardless of what it is called, so the following is valid as well:

    .. code-block:: python

        def __page__(remaining_path, /):
            ...



__settings__.py
+++++++++++++++

Configuration for your Blu app.

Should be placed in the root of the ``app/`` directory, i.e. the app directory should be the immediate parent directory of __settings__.py.

.. code-block:: python
    :caption: app/__settings__.py

    CLIENT_REQUIREMENTS = ['arrr', 'aiohttp']

You can configure your Blu app by creating a __settings__.py file and assigning configuration values at the top level of the file. For example, the __settings__.py file above sets the *CLIENT_REQUIREMENTS* configuration property to ``['arrr', 'aiohttp']``.

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
    :caption: app/greet_me/__index__.py

    from blu.html import p


    def __page__(*, my_name):
        return p['Hello ', my_name, '!']

.. code-block:: html
    :caption: GET /greet_me?my_name=Kevin

    <p>Hello Kevin!</p>

You can set default values for query parameters:

.. code-block:: python
    :caption: app/greet_me/__index__.py

    from blu.html import p


    def __page__(*, my_name='World'):
        return p['Hello ', my_name, '!']

.. code-block:: html
    :caption: GET /greet_me?my_name=Kevin

    <p>Hello World!</p>

You can also use ``**kwargs`` for query parameters:

.. code-block:: python
    :caption: app/greet_me/__index__.py

    from blu.html import p


    def __page__(*, my_name, **kwargs):
        greeting = kwargs.get('greeting', 'Hello')
        return p[greeting, ' ', my_name, '!']

.. code-block:: html
    :caption: GET /greet_me?my_name=Kevin&greeting=Hi

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
    :caption: GET /foo/bar/baz

    <p>Remaining path: bar/baz</p>

Blu passes these arguments in by position, so unlike route- and query-parameter-capturing arguments, they can have any name:

.. code-block:: python
    :caption: app/foo/__default__.py

    from blu.html import p

    def __page__(remaining_path, /):
        return p['Remaining path: ', remaining_path]


All Python Modules
------------------

The following module-level attribute has special meaning in any Python module under the ``app`` module:

.. py:data:: __client__
    :type: bool


.. code-block:: python

    from blu import client

    __client__ = True


    @client
    def Hello():
        return 'Hello, World!'


Set a module's ``__client__`` attribute to ``True`` in order to make the module available client-side.

If a module does not have a ``__client__`` attribute set to ``True``, it will not be available to run client-side. For example, trying to use the :func:`ClientElement <blu.ClientElement>` ``Hello`` shown in the following example will fail, because the user's browser will attempt to render ``Hello``, but will raise an :class:`ImportError` when trying to import ``Hello`` because the module it is in doesn't exist in the client environment:

.. code-block:: python

    from blu import client


    @client
    def Hello():
        return 'Hello, World!'

To fix this, use the ``__client__`` module attribute:

.. code-block:: python

    from blu import client

    __client__ = True


    @client
    def Hello():
        return 'Hello, World!'


Static Files
------------

Any non-Python file under the ``app/`` directory will be treated as a static file and will be served from the path it is at relative to the ``app/`` directory.

For example, if you have a text file at ``app/path/to/file.txt``, you will be able to download that file from ``/path/to/file.txt``.

.. note::

    Static files are served statically even if they are under a dynamic route. So if you have a file at ``app/_id_/file.txt``, then sending a request to ``/some-id/file.txt`` will result in an HTTP 404 error. Instead, you would access the file at ``/_id_/file.txt``.

Blu serves static files in production as well as in development, but if you want to serve static files from a separate service, you can access them in the ``static/`` directory (this will be in your project root, in the same parent directory as ``app/``) after :ref:`building your app for production<Building Your App>`.


