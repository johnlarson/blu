from blu import Response, session


def __page__():
    count = session.get("count", 0) + 1
    session["count"] = count
    return Response("ok", headers={"X-Count": str(count)})
