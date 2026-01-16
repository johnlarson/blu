from importlib import import_module
from blu._utils import asgi


from collections.abc import Generator
from blu._core.nodes import ClientElement, HTMLElement, Key, Node
from blu._utils.typing import Iterable
import mimetypes
from pathlib import Path

import aiofiles
from blu._app.router import NotFound, router_from_root_package
from blu._core.http import QueryParams, Request, Response
from blu._utils import asgi
from .render import render_to_str

import app as app_def

_router = router_from_root_package(app_def)


async def app(scope: asgi.Scope, receive: asgi.Receiver, send: asgi.Sender):
    if scope['type'] == 'lifespan':
        await _lifespan(scope, receive, send)
    elif scope['type'] == 'http':
        await _http(scope, receive, send)
    else:
        await _websocket(scope, receive, send)


async def _lifespan(
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
    scope: asgi.HTTPConnectionScope,
    receive: asgi.Receiver,
    send: asgi.Sender
):
    try:
        await _serve_static(scope, send)
    except NotFound:
        pass
    else:
        return
    request = await _create_request(scope)
    try:
        response = await _router.handle(request)
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
        'status': response._status,
        'headers': _get_headers(response)
    })
    body_str = await render_to_str(response._body)
    # await send({'type': 'http.response.body', 'body': b'Hello!'})
    await send({
        'type': 'http.response.body',
        'body': body_str.encode('utf-8'),
    })


async def _serve_static(
    scope: asgi.HTTPConnectionScope,
    send: asgi.Sender,
):
    if not _is_static_file(scope['path']):
        raise NotFound
    assert hasattr(app_def, '__path__')
    path_str = app_def.__path__[0]
    app_def_path = Path(path_str)
    file_path = app_def_path / scope['path'].strip('/')
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
    

def _is_static_file(url_path: str):
    if '__pycache__' in url_path:
        return False
    if url_path.strip().endswith('.py'):
        module_path = 'app.' + '.'.join(url_path.strip().split('/'))
        module = import_module(module_path)
        return getattr(module, '__client__', False)
    return True


def _get_headers(response: Response) -> Iterable[tuple[bytes, bytes]]:
    return [
        (b'Access-Control-Allow-Origin', b'https://micropython.org'),
        *[
            (k.encode('utf-8'), v.encode('utf-8'))
            for k, v in response._headers.items()
        ],
    ]


async def _create_request(scope: asgi.HTTPConnectionScope) -> Request:
    return Request(
        scope['path'],
        query=QueryParams.from_query_string(
            scope['query_string'].decode(),
        ),
        headers={k.decode(): v.decode() for k, v in scope['headers']},
    )


async def _websocket(
    scope: asgi.WSConnectionScope,
    receive: asgi.Receiver,
    send: asgi.Sender
):
    ...


async def get_page_node(path: str):
    response = await get_page_response(path)
    return response._body  # type: ignore


async def get_page_rendered(path: str):
    unrendered = await get_page_node(path)
    return render_page_node(unrendered)


async def get_page_response(path: str):
    if '?' in path:
        url_path, query_str = path.strip().split('?')
        request = Request(
            url_path,
            QueryParams.from_query_string(query_str)
        )
    else:
        request = Request(path)
    return await _router.handle(request)
    

type RenderedNode = (
    HTMLElement |
    str |
    int |
    float |
    bool |
    None
)


def render_page_node(root: Node) -> Node:
    ret_tuple = _render_page_node_rec(root)
    return ret_tuple[0] if len(ret_tuple) == 1 else ret_tuple


def _render_page_node_rec(root: Node) -> tuple[Node, ...]:
    uncollapsed = _render_page_nodes_rec(root)
    return _collapse_nodes(uncollapsed)


def _collapse_nodes(uncollapsed: Iterable[Node]) -> tuple[Node, ...]:
    current_str = ''
    collapsed: list[Node] = []
    for item in uncollapsed:
        if isinstance(item, str):
            current_str += item
        else:
            if current_str:
                collapsed.append(current_str)
                current_str = ''
            collapsed.append(item)
    if current_str:
        collapsed.append(current_str)
    return tuple(collapsed)


def _render_page_nodes_rec(root: Node) -> tuple[Node, ...]:
    if isinstance(root, ClientElement):
        return _render_client_element(root)
    if isinstance(root, HTMLElement):
        return _render_html_element(root)
    if isinstance(root, Key):
        return _render_key(root)
    if isinstance(root, Iterable) and not isinstance(root, str):
        return _render_iterable(root)
    if root is True:
        return ('true',)
    if root is False:
        return ('false',)
    if root is None:
        return ()
    return (str(root),)


def _render_client_element(element: ClientElement) -> tuple[Node, ...]:
    render_return = element._renderer(*element._args, **element._kwargs)  # type: ignore
    if isinstance(render_return, Generator):
        next(render_return)
        try:
            render_return.send(element._children)
        except StopIteration as e:
            render_return = e.value
    return _render_page_node_rec(render_return)


def _render_html_element(element: HTMLElement) -> tuple[Node, ...]:
    return (element[_render_iterable(element._children)],)


def _render_key(key: Key) -> tuple[Node, ...]:
    return _render_iterable(key._children)  # type: ignore


def _render_iterable(root: Node) -> tuple[Node, ...]:
    tuples = [_render_page_node_rec(x) for x in root]  # type: ignore
    return _collapse_nodes(y for x in tuples for y in x)