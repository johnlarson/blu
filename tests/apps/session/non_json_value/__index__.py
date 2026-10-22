from blu import session


def __page__():
    session["a"] = object()
    return "ok"
