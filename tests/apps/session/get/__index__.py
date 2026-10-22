from blu import Response, session


def __page__():
    return Response(
        "ok",
        headers={
            "X-Get-Default": str(session.get("missing")),
            "X-Get-Fallback": str(session.get("missing", "fallback")),
            "X-Get-Count": str(session.get("count")),
        },
    )
