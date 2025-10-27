.. note::
    
    Calling a client element as a function does not immediately result in its rendering function being called; that call is deferred until the element is rendered on the client.

.. note::
    
    Calling a client element as a function does not mutate the original client element; instead, it returns a copy of the original client element with the new render arguments.

    .. code-block:: python

        from blu import client
        from blu.html import p

        __client__ = True


        @client
        Greeting(name):
            return p[f'Hello, {name}!']

        original = Greeting('Adam')
        copy = original('Brittany')

        original  # <p>Hello, Adam!</p>
        copy  # <p>Hello, Brittany!</p>

.. note::

    Calling a client element as a function completely replaces any existing render arguments.

    .. code-block:: python

        from blu import client
        from blu.html import p

        __client__ = True


        @client
        MyClientElement(a, b=2):
            return p[f'{a},{b}']
        

        original = MyClientElement(3, b=4)
        copy = original(1)

        original  # <p>3,4</p>
        copy  # <p>1,2</p>