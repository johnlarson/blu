from blu._react.types import Node
from blu._utils.typing import Iterable
import mimetypes
from pathlib import Path
from blu._utils.typing import Optional

import aiofiles
from blu._app.asgi_app.router import NotFound, Router, router_from_root_package_name
from blu._http import QueryParams, Request, Response
from blu._react._render import Renderer
from blu._utils import asgi


class ASGIApp(asgi.App):
    _router: Router
    _renderer: Renderer
    _static_dir: Path
    
    def __init__(self, app: str, static_dir: Path, project: Optional[Path]):
        self._router = router_from_root_package_name(app)
        self._renderer = Renderer(static_dir=static_dir)
        self._static_dir = static_dir

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
        try:
            await self._serve_static(scope, send)
        except NotFound:
            pass
        else:
            return
        request = await self._create_request(scope)
        try:
            response = await self._router.handle(request)
        except NotFound:
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
        # await send({'type': 'http.response.body', 'body': b'Hello!'})
        await send({
            'type': 'http.response.body',
            'body': body_str.encode('utf-8'),
        })
    
    async def _serve_static(
        self,
        scope: asgi.HTTPConnectionScope,
        send: asgi.Sender,
    ):
        file_path = self._static_dir / scope['path'].strip('/')
        content_type, _ = mimetypes.guess_type(file_path)
        headers = (
            [] if content_type is None
            else [(b'Content-Type', content_type.encode('utf-8'))]
        )
        try:
            async with aiofiles.open(file_path, 'rb') as file:
                await send({
                    'type': 'http.response.start',
                    'status': 200,
                    'headers': headers,
                    'trailers': False,
                })
                async for chunk in file:
                    await send({
                        'type': 'http.response.body',
                        'body': chunk,
                        'more_body': True,
                    })
                await send({
                    'type': 'http.response.body',
                    'body': b'',
                    'more_body': False,
                })
        except (FileNotFoundError, IsADirectoryError):
            raise NotFound

    def _get_headers(
        self,
        response: Response,
    ) -> Iterable[tuple[bytes, bytes]]:
        return [
            (b'Access-Control-Allow-Origin', b'https://micropython.org'),
            *[
                (k.encode('utf-8'), v.encode('utf-8'))
                for k, v in response.headers.items()
            ],
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

    async def get_page_node(self, path: str):
        response = await self.get_page_response(path)
        return response._body  # type: ignore

    async def get_page_rendered(self, path: str):
        unrendered = await self.get_page_node(path)
        return _render_page_node(unrendered)
    
    async def get_page_response(self, path: str):
        if '?' in path:
            url_path, query_str = path.strip().split('?')
            request = Request(
                url_path,
                QueryParams.from_query_string(query_str)
            )
        else:
            request = Request(path)
        return await self._router.handle(request)


def _render_page_node(root: Node) -> Node:
    return root