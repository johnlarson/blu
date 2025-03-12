from collections.abc import Iterable
from pathlib import Path
from typing import Optional
from blu._app.asgi_app.router import Router, router_from_root_package_name
from blu._http import QueryParams, Request, Response
from blu._react._render import Renderer
from blu._utils import asgi


class ASGIApp(asgi.App):
    _router: Router
    _renderer: Renderer
    
    def __init__(self, app: str, project: Optional[Path]):
        self._router = router_from_root_package_name(app)
        self._renderer = Renderer(root_dir=project)

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
        event = await receive()
        assert event['type'] == 'lifespan.startup'
        await send({'type': 'lifespan.startup.complete'})
        event = await receive()
        assert event['type'] == 'lifespan.shutdown'
        await send({'type': 'lifespan.shutdown.complete'})


    async def _http(
        self,
        scope: asgi.HTTPConnectionScope,
        receive: asgi.Receiver,
        send: asgi.Sender
    ):
        request = await self._create_request(scope)
        path = request.path
        stripped = path.strip('/')
        segments: list[str] = [] if stripped == '' else stripped.split('/')
        response = await self._router.handle(request, segments)
        if response is None:
            await send({
                'type': 'http.response.start',
                'status': 404,
            })
            await send({
                'type': 'http.response.body',
                'body': b'Not Found: ' + scope['path'].encode('utf-8'),
            })
            return
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
        return Request(
            scope['path'],
            query=QueryParams.from_query_string(
                scope['query_string'].decode(),
            ),
            headers={k.decode(): v.decode() for k, v in scope['headers']},
        )

    async def _websocket(
        self,
        scope: asgi.WSConnectionScope,
        receive: asgi.Receiver,
        send: asgi.Sender
    ):
        ...