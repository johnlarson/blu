from blu import Response, session


def __page__():
    return Response("ok", headers={"X-Count": str(session["count"])})
