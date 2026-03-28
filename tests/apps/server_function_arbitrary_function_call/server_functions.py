from blu import server

callable_called = [False]


@server
def callable():
    callable_called[0] = True
    return "Callable"


non_callable_called = [False]


def should_not_be_callable():
    non_callable_called[0] = True
    return "Should not be callable"
