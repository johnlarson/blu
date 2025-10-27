.. note::

    Why does the code in the previous example include the line ``__client__ = True``?
    
    By default, none of the `.py` files in your app will be sent to the user's web browser and therefore cannot be run client-side. To allow a module to run client-side, you must explicitly mark it by setting the module-level attribute ``__client__`` to ``True``.

    In order for the client element to be rendered client-side, the code to do so must be available to the user's web browser, so the module where the client element is found, as well as any of its dependencies, must include ``__client__ = True``.

    If you're familiar with full stack React frameworks for JavaScript, note that this is *not* the same as the ``"use client"`` directive in JavaScript React applications.

.. note::
    
    Client elements cannot be created from asynchronous functions.

    .. code-block:: python

        from blu import client
        from blu.html import p

        # Wrong!
        @client
        async def Hello():
            return p['Hello, World!']

        
        # Right.
        @client
        def Hello():
            return p['Hello, World!']


.. note::

    Client-side code runs in a different environment than server-side code. If your client-side code uses an external library, make sure it is installed in the client environment by adding it to the list of client dependencies in ``app/__settings__.py`` (if the ``__settings__.py`` doesn't exist, create it)::

        app/
          __index__.py
          __settings__.py

    .. code-block:: python
        :caption: app/__index__.py

        import arrr
        from blu import client

        __client__ = True


        def __page__():
            return MyClientElement
        

        @client
        def MyClientElement():
            return p[
                arrr.translate('Hello there. How are you?')
            ]


    .. code-block:: python
        :caption: app/__settings__.py

        CLIENT_REQUIREMENTS = ['arrr']


.. note::

    Client-side code runs in a different environment than server-side code. If your client-side code uses dependencies that aren't available on the server, make sure you check the environment before importing those dependencies:

    .. code-block:: python
        :caption: Wrong!
        :emphasize-lines: 4

        from blu import client
        from blu.html import button
        
        from pyscript import window

        __client__ = True


        def __page__():
            return GoToPyPIButton

        
        @client
        def GoToPythonDotOrgButton():
            return button(onClick=navigate_to_python_dot_org)

        
        def navigate_to_python_dot_org(e):
            window.location = 'https://www.python.org'

    .. code-block:: python
        :caption: Right.
        :emphasize-lines: 4-5

        from blu import running_on_client
        from blu.html import button
        
        if is_client:
            from pyscript import window

        __client__ = True


        def __page__():
            return GoToPyPIButton

        
        @client
        def GoToPythonDotOrgButton():
            return button(onClick=navigate_to_python_dot_org)

        
        def navigate_to_python_dot_org(e):
            window.location = 'https://www.python.org'