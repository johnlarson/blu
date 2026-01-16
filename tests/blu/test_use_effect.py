def test_generator_function_callback():
    """
    If the callback is a generator function, it will be run up until the
    first yield right after initial render. The remainder will be run
    right before the element is removed from the DOM.
    """
    ...


def test_non_generator_function_callback():
    """
    If the callback is not a generator function, it will be called right
    after the element is initially rendered to the DOM.
    """
    ...


def test_generator_function_not_called_on_rerender():
    """
    For generator function callbacks, the teardown and setup will not be
    performed on a re-render. The setup will only occur once just after
    the element is rendered to the DOM, and the teardown will only occur
    once just before the element is removed from the DOM.
    """
    ...



def test_non_generator_function_not_called_on_rerender():
    """
    For callbacks that are not generator functions, the callback will
    not be called again on a re-render; it will only be called once,
    right after the element is added to the DOM.
    """
    ...
