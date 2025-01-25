from blu._utils import asgi


async def app(scope: asgi.Scope, receive: asgi.Receiver, send: asgi.Sender):
    ...