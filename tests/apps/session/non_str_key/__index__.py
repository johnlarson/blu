from blu import session


def __page__():
    session[1] = "value"  # type: ignore[index]
    return "ok"
