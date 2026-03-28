called = [False]


def server_only_function():
    called[0] = True
    return "This should only have been called "
