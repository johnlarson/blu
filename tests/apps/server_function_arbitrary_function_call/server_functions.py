from blu import server

callable_called = [False]


@server
def callable(value: str) -> str:
    callable_called[0] = True
    return value


non_callable_called = [False]


def should_not_be_callable() -> str:
    non_callable_called[0] = True
    return "Should not have been called"
