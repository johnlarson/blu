import ast
from functools import cache
from importlib import import_module
import shutil
from tempfile import TemporaryDirectory
from types import ModuleType
from zipfile import ZipFile
import zipfile
from blu._exceptions import WrongEnvironmentError
from blu._utils import asgi


from collections.abc import Generator
from blu._nodes import ClientElement, HTMLElement, Key, Node
from blu._utils.typing import Iterable
import mimetypes
from pathlib import Path

import aiofiles
from blu._app.router import NotFound, router_from_root_package
from blu._http import QueryParams, Request, Response
from blu._utils import asgi
from .render import render_to_str
from blu import _utils


async def app(scope: asgi.Scope, receive: asgi.Receiver, send: asgi.Sender):
    """
    An `ASGI <https://asgi.readthedocs.io/en/latest/>`_ app that runs
    the Blu application defined in your current Python environment's
    ``app`` package (for most ASGI servers, running the server in the
    parent directory of your project's ``app`` directory will put your
    project's ``app`` package in the Python environment).

    .. code-block:: console

        $ uvicorn blu:app

    .. code-block:: console

        $ hypercorn blu:app

    .. code-block:: console

        $ daphne blu:app
    """
    if _utils.is_client:
        raise WrongEnvironmentError(
            "Cannot call Blu ASGI app in a client environment.",
        )
    if scope["type"] == "lifespan":
        await _lifespan(scope, receive, send)
    elif scope["type"] == "http":
        await _http(scope, receive, send)
    else:
        await _websocket(scope, receive, send)


async def _lifespan(
    scope: asgi.LifespanScope, receive: asgi.Receiver, send: asgi.Sender
):
    event = await receive()
    assert event["type"] == "lifespan.startup"
    await send({"type": "lifespan.startup.complete"})
    event = await receive()
    assert event["type"] == "lifespan.shutdown"
    await send({"type": "lifespan.shutdown.complete"})


PYTHON_MIME = "text/x-python"
ZIP_MIME = "text/zip"


async def _http(
    scope: asgi.HTTPConnectionScope, receive: asgi.Receiver, send: asgi.Sender
):
    if scope["path"] == "/_blu_internal/app_pkg.zip":
        path = _python_zip_dir() / "app.zip"
        await _serve_file(path, ZIP_MIME, send)
        return
    if scope["path"] == "/_blu_internal/blu_pkg.zip":
        path = _python_zip_dir() / "blu.zip"
        await _serve_file(path, ZIP_MIME, send)
        return
    if scope["path"] == "/_blu_internal/client_main.py":
        path = Path(__file__).parent / "client_main.py"
        await _serve_file(path, PYTHON_MIME, send)
        return
    try:
        await _serve_static(scope, send)
    except NotFound:
        pass
    else:
        return
    request = await _create_request(scope)
    try:
        response = await _get_router().handle(request)
    except NotFound:
        await _serve_404("Not Found: " + scope["path"], send)
        return
    await send(
        {
            "type": "http.response.start",
            "status": response._status,
            "headers": _get_headers(response),
        }
    )
    body_str = await render_to_str(response._body)
    # await send({'type': 'http.response.body', 'body': b'Hello!'})
    await send(
        {
            "type": "http.response.body",
            "body": body_str.encode("utf-8"),
        }
    )


async def _serve_404(message: str, send: asgi.Sender):
    await send(
        {
            "type": "http.response.start",
            "status": 404,
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": message.encode(),
        }
    )


async def _serve_static(
    scope: asgi.HTTPConnectionScope,
    send: asgi.Sender,
):
    if not _is_static_file(scope["path"]):
        raise NotFound
    app_def = _get_app_def()
    assert hasattr(app_def, "__path__")
    path_str = app_def.__path__[0]
    app_def_path = Path(path_str)
    file_path = app_def_path / scope["path"].strip("/")
    content_type, _ = mimetypes.guess_type(file_path)
    try:
        await _serve_file(file_path, content_type, send)
    except (FileNotFoundError, IsADirectoryError):
        raise NotFound


async def _serve_file(path: Path, content_type: str | None, send: asgi.Sender):
    headers = (
        []
        if content_type is None
        else [(b"Content-Type", content_type.encode("utf-8"))]
    )
    async with aiofiles.open(path, "rb") as file:
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": headers,
                "trailers": False,
            }
        )
        async for chunk in file:
            await send(
                {
                    "type": "http.response.body",
                    "body": chunk,
                    "more_body": True,
                }
            )
        await send(
            {
                "type": "http.response.body",
                "body": b"",
                "more_body": False,
            }
        )


def _is_static_file(url_path: str):
    if "__pycache__" in url_path:
        return False
    if url_path.strip().endswith(".py"):
        return False
    return True


def _get_headers(response: Response) -> Iterable[tuple[bytes, bytes]]:
    return [
        (b"Access-Control-Allow-Origin", b"https://micropython.org"),
        *[(k.encode("utf-8"), v.encode("utf-8")) for k, v in response._headers.items()],
    ]


async def _create_request(scope: asgi.HTTPConnectionScope) -> Request:
    return Request(
        scope["path"],
        query=QueryParams.from_query_string(
            scope["query_string"].decode(),
        ),
        headers={k.decode(): v.decode() for k, v in scope["headers"]},
    )


async def _websocket(
    scope: asgi.WSConnectionScope, receive: asgi.Receiver, send: asgi.Sender
): ...


async def get_page_node(path: str):
    response = await get_page_response(path)
    return response._body  # type: ignore


async def get_page_rendered(path: str):
    unrendered = await get_page_node(path)
    return render_page_node(unrendered)


async def get_page_response(path: str):
    if "?" in path:
        url_path, query_str = path.strip().split("?")
        request = Request(url_path, QueryParams.from_query_string(query_str))
    else:
        request = Request(path)
    return await _get_router().handle(request)


type RenderedNode = (HTMLElement | str | int | float | bool | None)


def render_page_node(root: Node) -> Node:
    ret_tuple = _render_page_node_rec(root)
    return ret_tuple[0] if len(ret_tuple) == 1 else ret_tuple


def _render_page_node_rec(root: Node) -> tuple[Node, ...]:
    uncollapsed = _render_page_nodes_rec(root)
    return _collapse_nodes(uncollapsed)


def _collapse_nodes(uncollapsed: Iterable[Node]) -> tuple[Node, ...]:
    current_str = ""
    collapsed: list[Node] = []
    for item in uncollapsed:
        if isinstance(item, str):
            current_str += item
        else:
            if current_str:
                collapsed.append(current_str)
                current_str = ""
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
        return ("true",)
    if root is False:
        return ("false",)
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


@cache
def _get_router():
    app_def = _get_app_def()
    return router_from_root_package(app_def)


@cache
def _get_app_def():
    import app

    return app


async def _serve_app_module(
    scope: asgi.HTTPConnectionScope,
    send: asgi.Sender,
):
    rel_path = scope["path"].replace("/_blu_internal/app_module/", "")
    stripped_rel_path = rel_path.strip("/")
    import app

    assert app.__spec__ is not None
    app_pkg_locations = app.__spec__.submodule_search_locations
    assert app_pkg_locations
    app_pkg_path = Path(app_pkg_locations[0])
    parts = Path(stripped_rel_path).parts
    assert ".." not in parts
    assert "__pycache__" not in parts
    assert "*" not in str(stripped_rel_path)
    try:
        path = app_pkg_path / (stripped_rel_path + ".py")
        source_code = path.read_text()
    except FileNotFoundError:
        try:
            path = app_pkg_path / stripped_rel_path / "__init__.py"
            source_code = path.read_text()
        except FileNotFoundError:
            await _serve_404("", send)
            return
    parsed = ast.parse(source_code)
    for stmt in ast.iter_child_nodes(parsed):
        if isinstance(stmt, ast.Assign):
            stmt_source = ast.get_source_segment(source_code, stmt)
            if stmt_source == "__client__ = True":
                parts = path.parts
                await _serve_module(path, send)
                return
    await _serve_404("", send)


async def _serve_blu_module(
    scope: asgi.HTTPConnectionScope,
    send: asgi.Sender,
):
    url_path_stripped = scope["path"].strip("/")
    parts = Path(url_path_stripped).parts
    assert ".." not in parts
    assert "__pycache__" not in parts
    assert "*" not in url_path_stripped
    rel_path = url_path_stripped.replace("_blu_internal/blu_module", "")
    stripped_rel_path = rel_path.strip("/")
    blu_root = Path(__file__).parent.parent
    try:
        path = blu_root / (stripped_rel_path + ".py")
        await _serve_module(path, send)
    except FileNotFoundError:
        path = blu_root / stripped_rel_path / "__init__.py"
        await _serve_module(path, send)


async def _serve_module(path: Path, send: asgi.Sender):
    await _serve_file(path, "text/x-python", send)


@cache
def _python_zip_dir():
    ret = Path(TemporaryDirectory().name)
    _blu_pkg_zip(ret)
    _app_pkg_zip(ret)
    return ret


def _blu_pkg_zip(zips_root: Path):
    print("BLU ZIP")
    src_dir = Path(__file__).parent.parent
    base_name = str(zips_root / "blu")
    shutil.make_archive(base_name, "zip", src_dir, src_dir)


def _app_pkg_zip(zips_root: Path):
    print("APP ZIP")
    import app

    assert app.__spec__ is not None
    app_pkg_locations = app.__spec__.submodule_search_locations
    assert app_pkg_locations
    src_path = Path(app_pkg_locations[0])
    dest_path = zips_root / "app.zip"
    with ZipFile(dest_path, "w") as dest_f:
        for path in src_path.rglob("*"):
            if path.is_file():
                if _is_client_module(path):
                    dest_f.write(str(path), arcname=path.relative_to(src_path))
    print("DONE ZIPPING")


def _is_client_module(path: Path) -> bool:
    if path.suffix != ".py":
        return False
    source_code = path.read_text()
    parsed = ast.parse(source_code)
    for stmt in ast.iter_child_nodes(parsed):
        if isinstance(stmt, ast.Assign):
            stmt_source = ast.get_source_segment(source_code, stmt)
            if stmt_source == "__client__ = True":
                return True
    return False
