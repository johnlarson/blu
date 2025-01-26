from blu._utils import asgi


async def call_asgi(
    scope: asgi.Scope,
    receive: asgi.Receiver,
    send: asgi.Sender,
):
    ...