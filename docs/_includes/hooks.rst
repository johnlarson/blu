Blu is a React framework, and React provides a special type of function called a *hook*. These are the functions you import from Blu whose names start with ``use``. They are used for managing UI state and adding callbacks for lifecycle phases, and there are certain restrictions on how they can be used:

1. A hook can only be called in the scope of a client element's rendering function body, or the scope of a custom hook's function body (a *custom hook* is any function whose name starts with ``use`` that calls other hooks).
2. A client element rendering function or custom hook must call the same hooks in the same order *every time* the rendering function or custom hook is called. The best way to follow this rule is just to never call a hook in a conditional block or loop.

Breaking either of these rules will result in undefined behavior.

.. code-block:: python

    from blu import client, use_ref
    from blu.html import p


    # Wrong! This function is not a client element or custom hook, so
    # it can't call hooks.
    def some_function():
        some_ref = use_ref()
    

    # Right. This is a client element whose rendering function calls
    # the use_ref hook.
    @client
    def SomeClientElement():
        some_ref = use_ref()
        return p['(client element content)']

    
    # Right. Because this function's name starts with "use", it is a
    # valid custom hook and can call other hooks.
    def use_some_hook():
        return use_ref()

    
    # Wrong! Hook called in a conditional block.
    @client
    def SomeClientElement(some_condition):
        if some_condition:
            my_ref = use_ref()
        else:
            my_ref = None
        return p['(client element content)']
    
    
    # Wrong! Hook called in a conditional block.
    def use_some_hook(some_condition):
        if some_condition:
            return None
        else:
            return use_ref()
    

    # Wrong! Hook called in a loop.
    def use_some_hook(some_list):
        result = []
        for item in some_list:
            result.append(use_ref())
        return result
    
    
    # Wrong! Hook called in a loop.
    @client
    def SomeClientElement(num_iterations):
        i = 0
        while i < num_iterations:
            my_ref = use_ref()
        return p['(client element content)']

    
    # Wrong! use_my_custom_hook is a custom hook, so it must *not* be
    # called in a conditinal block.
    @client
    def SomeClientElement(some_condition):
        if some_condition:
            value = use_my_custom_hook()
        else:
            value = None
        return p['(client element content)']


    def use_my_custom_hook():
        return use_ref()