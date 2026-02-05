from blu import Response


def __page__():
    return Response("BODY", 401, {"A": "b"})
