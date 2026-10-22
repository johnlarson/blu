import ast
from collections.abc import Generator
from functools import cache
import mimetypes
from pathlib import Path
from tempfile import mkdtemp
from zipfile import ZipFile

import asyncio

from blu._exceptions import WrongEnvironmentError
from blu._utils import asgi
from blu._app.router import NotFound, router_from_root_package
from blu._http import QueryParams, Request, Response
from blu._server_functions import (
    collect_blu_server_import_bindings,
    decorator_is_server,
)
from blu._utils import asgi
from blu._nodes import ClientElement, HTMLElement, Key, Node
from blu._micropython.typing import Iterable, Union
from blu import _utils
from .render import render_to_str


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
    from blu._server_functions import refresh_server_function_registry

    refresh_server_function_registry()
    await send({"type": "lifespan.startup.complete"})
    event = await receive()
    assert event["type"] == "lifespan.shutdown"
    await send({"type": "lifespan.shutdown.complete"})


PYTHON_MIME = "text/x-python"
ZIP_MIME = "text/zip"
JS_MIME = "text/javascript"


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
    if scope["path"].startswith("/_blu_internal/static/"):
        subpath = scope["path"].removeprefix("/_blu_internal/static/")
        await _serve_blu_static_file(subpath, send)
        return
    if scope["path"] == "/_blu_internal/server_function":
        if scope["method"] != "POST":
            await _serve_405(send)
            return
        headers = _get_asgi_headers(scope)
        if headers.get("content-type", None) != "application/json":
            await _serve_415(send)
            return
        from blu._server_functions import handle_server_function_request

        await handle_server_function_request(receive, send)
        return
    try:
        await _serve_static(scope, send)
    except NotFound:
        pass
    else:
        return
    request = await _create_request(scope)
    from blu._session import bind_session, unbind_session

    session_token = bind_session(request.headers.get("cookie"))
    try:
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
        await send(
            {
                "type": "http.response.body",
                "body": body_str.encode("utf-8"),
            }
        )
    finally:
        unbind_session(session_token)


async def _serve_blu_static_file(subpath: str, send: asgi.Sender):
    file_path = Path(__file__).parent.parent / "_blu_static_files" / subpath
    content_type, _ = mimetypes.guess_type(file_path)
    await _serve_file(file_path, content_type, send)


def _get_asgi_headers(scope: asgi.HTTPConnectionScope) -> dict[str, str]:
    return {k.decode("utf-8"): v.decode("utf-8") for k, v in scope["headers"]}


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


async def _serve_405(send: asgi.Sender):
    await send(
        {
            "type": "http.response.start",
            "status": 405,
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": b"",
        }
    )


async def _serve_415(send: asgi.Sender):
    await send(
        {
            "type": "http.response.start",
            "status": 415,
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": b"",
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
    await (await asyncio.to_thread(_serve_file_thread, path, content_type, send))


async def _serve_file_thread(path: Path, content_type: str | None, send: asgi.Sender):
    headers = (
        []
        if content_type is None
        else [(b"Content-Type", content_type.encode("utf-8"))]
    )
    with open(path, "rb") as file:
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": headers,
                "trailers": False,
            }
        )
        for chunk in file:
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
    from blu._session import session_cookie_header

    headers: list[tuple[bytes, bytes]] = [
        (b"Access-Control-Allow-Origin", b"https://micropython.org"),
        *[(k.encode("utf-8"), v.encode("utf-8")) for k, v in response._headers.items()],
    ]
    cookie = session_cookie_header()
    if cookie is not None:
        headers.append((b"set-cookie", cookie.encode("utf-8")))
    return headers


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


RenderedNode = Union[HTMLElement, str, int, float, bool, None]


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


@cache
def _python_zip_dir():
    # mkdtemp (not TemporaryDirectory) so the dir survives for the process;
    # TemporaryDirectory().name is cleaned up as soon as the object is dropped.
    ret = Path(mkdtemp())
    _blu_pkg_zip(ret)
    _app_pkg_zip(ret)
    return ret


def _blu_pkg_zip(zips_root: Path):
    src_dir = Path(__file__).parent.parent
    dest_path = zips_root / "blu.zip"
    with ZipFile(dest_path, "w") as dest_f:
        for path in src_dir.rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            dest_f.write(path, arcname=path.relative_to(src_dir).as_posix())


def _app_pkg_zip(zips_root: Path):
    import app

    assert app.__spec__ is not None
    app_pkg_locations = app.__spec__.submodule_search_locations
    assert app_pkg_locations
    src_path = Path(app_pkg_locations[0])
    dest_path = zips_root / "app.zip"
    with ZipFile(dest_path, "w") as dest_f:
        added_py: set[str] = set()
        for path in src_path.rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            rel_posix = path.relative_to(src_path).as_posix()
            if path.suffix == ".py":
                if _is_client_module(path):
                    dest_f.write(path, arcname=rel_posix)
                    added_py.add(rel_posix)
        for path in src_path.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            rel_posix = path.relative_to(src_path).as_posix()
            if rel_posix in added_py:
                continue
            stub_src = _client_stub_source_for_server_module(path)
            if stub_src is not None:
                dest_f.writestr(rel_posix, stub_src.encode("utf-8"))


def _client_stub_source_for_server_module(path: Path) -> str | None:
    try:
        source = path.read_text()
    except OSError:
        return None
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    blu_pkg, server_dec = collect_blu_server_import_bindings(tree.body)
    chunks: list[str] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not any(
                decorator_is_server(d, blu_pkg, server_dec) for d in node.decorator_list
            ):
                continue
            async_kw = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
            args_src = ast.unparse(node.args)
            chunks.append(f"@server\n{async_kw}def {node.name}({args_src}):\n    ...")
    if not chunks:
        return None
    return "from blu import server\n\n" + "\n\n".join(chunks) + "\n"


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
