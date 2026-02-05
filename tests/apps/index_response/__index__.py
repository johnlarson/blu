from blu import Response


def __page__():
    return Response("body", 401, {"Name": "value"})
