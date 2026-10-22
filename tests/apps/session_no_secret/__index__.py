from blu import session


def __page__():
    session["a"] = 1
    return "Hello"
