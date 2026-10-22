from blu import Response, session


def __page__():
    session["marker"] = "client-readable-marker-42"
    return Response("ok")
