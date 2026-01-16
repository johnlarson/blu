from blu import Response
from blu.html import p


def __page__():
    return Response(
        p['Hello.'],
        status=404,
        headers={
            'Cache-Control': 'no-cache',
            'Last-Modified': 'Tue, 10 Dec 2024 10:00:00 GMT',
        },
    )