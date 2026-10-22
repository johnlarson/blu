from blu import Response, session


def __page__(*, action):
    if action == "set":
        session["data"] = {"nums": [1, 2], "ok": True}
        return Response("ok")
    return Response(
        "ok",
        headers={"X-Data": str(session["data"])},
    )
