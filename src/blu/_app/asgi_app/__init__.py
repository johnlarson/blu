from collections.abc import Iterable
from pathlib import Path
from blu._app.asgi_app.router import Router
from blu._http import Request, Response
from blu._react._render import Renderer
from blu._utils import asgi


class ASGIApp(asgi.App):
    _router: Router
    _renderer: Renderer
    
    def __init__(self, app: str, project: Path):
        ...

    async def __call__(
        self,
        scope: asgi.Scope,
        receive: asgi.Receiver,
        send: asgi.Sender
    ):
        if scope['type'] == 'lifespan':
            await self._lifespan(scope, receive, send)
        elif scope['type'] == 'http':
            await self._http(scope, receive, send)
        else:
            await self._websocket(scope, receive, send)
    
    async def _lifespan(
        self,
        scope: asgi.LifespanScope,
        receive: asgi.Receiver,
        send: asgi.Sender
    ):
        ...


    async def _http(
        self,
        scope: asgi.HTTPConnectionScope,
        receive: asgi.Receiver,
        send: asgi.Sender
    ):
        request = await self._create_request(scope)
        response = await self._router.handle(request, '')
        await send({
            'type': 'http.response.start',
            'status': response.status,
            'headers': self._get_headers(response)
        })
        body_str = await self._renderer.render_to_str(response.body)
        await send({
            'type': 'http.response.body',
            'body': body_str.encode('utf-8'),
        })

    def _get_headers(
        self,
        response: Response,
    ) -> Iterable[tuple[bytes, bytes]]:
        return [
            (k.encode('utf-8'), v.encode('utf-8'))
            for k, v in response.headers.items()
        ]

    async def _create_request(self, scope: asgi.HTTPConnectionScope) -> Request:
        ...

    async def _websocket(
        self,
        scope: asgi.WSConnectionScope,
        receive: asgi.Receiver,
        send: asgi.Sender
    ):
        ...