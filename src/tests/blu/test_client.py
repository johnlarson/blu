def test_args_passed_to_rendering_function():
    """
    Positional arguments passed into ClientElement.__call__ are passed
    on to provided rendering function.
    """
    ...


def test_kwargs_passed_to_rendering_function():
    """
    Keyword arguments passed into ClientElement.__call__ are passed on
    to provided rendering function.
    """
    ...


def test_no_arguments():
    """
    If ClientElement.__call__ is never called, renders without passing
    in any arguments to rendering function.
    """
    ...


def test_children_sent_to_rendering_function():
    """
    If the provided rendering function is a generator function, children
    passed into ClientElement.__getitem__ are sent to the generator
    returned by the rendering function when it yields.
    """
    ...


def test_no_children_generator():
    """
    If the provided rendering function is a generator function and the
    element has no children, nothing will be rendered where the render
    function's yield statement is.
    """
    ...
