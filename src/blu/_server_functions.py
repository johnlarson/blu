import ast
import asyncio
import base64
import functools
import importlib
import importlib.util
import inspect
import json
import pickle
from collections.abc import Awaitable, Callable, Sequence
from pathlib import Path
from typing import Any

from blu._utils.client import is_client

_BLU_SERVER_FN_ATTR = "_blu_is_server_function"


def _is_registered_server_function(fn: Any) -> bool:
    return getattr(fn, _BLU_SERVER_FN_ATTR, False)


def collect_blu_server_import_bindings(
    body: Sequence[ast.stmt],
) -> tuple[frozenset[str], frozenset[str]]:
    """
    From a module's top-level statements, collect local names that refer to the
    ``blu`` package and to :func:`blu.server`.

    Only absolute imports are considered (``level == 0``). ``from blu… import
    server`` (and ``server`` re-exported from ``blu.*`` submodules) binds the
    decorator name; ``import blu`` / ``import blu as …`` binds the package
    for ``@blu.server`` / ``@alias.server``.
    """
    blu_pkg: set[str] = set()
    server_decorator: set[str] = set()
    for stmt in body:
        if isinstance(stmt, ast.Import):
            for alias in stmt.names:
                if alias.name == "blu":
                    blu_pkg.add(alias.asname or "blu")
        elif isinstance(stmt, ast.ImportFrom):
            if stmt.level != 0:
                continue
            mod = stmt.module
            if mod is None or mod != "blu":
                continue
            for alias in stmt.names:
                if alias.name == "*":
                    continue
                if alias.name == "server":
                    server_decorator.add(alias.asname or "server")
    return frozenset(blu_pkg), frozenset(server_decorator)


def decorator_is_server(
    dec: ast.expr,
    blu_pkg_names: frozenset[str],
    server_decorator_names: frozenset[str],
) -> bool:
    """Whether ``dec`` applies :func:`blu.server` given import-derived name sets."""
    if isinstance(dec, ast.Name):
        return dec.id in server_decorator_names
    if isinstance(dec, ast.Call):
        return decorator_is_server(dec.func, blu_pkg_names, server_decorator_names)
    if isinstance(dec, ast.Attribute):
        if dec.attr != "server":
            return False
        if isinstance(dec.value, ast.Name):
            return dec.value.id in blu_pkg_names
        return False
    return False


def _read_module_source_without_importing_target(module_name: str) -> str | None:
    """
    Read the source file for ``module_name`` using :func:`importlib.util.find_spec`
    so we resolve the same path :func:`importlib.import_module` would use (including
    when ``app`` is a namespace package with several search locations), without
    executing that module's body.
    """
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        return None
    origin = spec.origin
    if origin not in (None, "namespace") and getattr(spec, "has_location", True):
        path = Path(origin)
        if path.suffix == ".py":
            try:
                return path.read_text(encoding="utf-8")
            except OSError:
                return None
    subs = getattr(spec, "submodule_search_locations", None)
    if subs:
        loc = Path(next(iter(subs)))
        try:
            return (loc / "__init__.py").read_text(encoding="utf-8")
        except OSError:
            return None
    return None


def _source_defines_top_level_server_function(source: str, fn_name: str) -> bool:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    blu_pkg, server_dec = collect_blu_server_import_bindings(tree.body)
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name != fn_name:
            continue
        return any(
            decorator_is_server(d, blu_pkg, server_dec) for d in node.decorator_list
        )
    return False


def _allowed_server_rpc_target(module_name: str, fn_name: str) -> bool:
    """
    True if ``module_name`` / ``fn_name`` is a top-level ``@server`` function
    according to the module's source, without importing that target module.
    """
    if not fn_name.isidentifier():
        return False
    if not module_name.startswith("app.") or module_name == "app":
        return False
    rest = module_name[4:]
    if not rest or not all(p.isidentifier() for p in rest.split(".")):
        return False
    source = _read_module_source_without_importing_target(module_name)
    if source is None:
        return False
    return _source_defines_top_level_server_function(source, fn_name)


async def _invoke_server_function_remote(
    module: str,
    name: str,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Any:
    from pyodide.http import pyfetch  # type: ignore

    payload = json.dumps(
        {"module": module, "name": name, "args": list(args), "kwargs": kwargs}
    )
    response = await pyfetch(
        "/_blu_internal/server_function",
        method="POST",
        body=payload,
        headers={"Content-Type": "application/json"},
    )
    text = await response.string()
    data = json.loads(text)
    if not data.get("ok"):
        raise RuntimeError(data.get("error", "server function call failed"))
    return pickle.loads(base64.b64decode(data["result_b64"]))


def _wrap_client(callable: Callable[..., Any]) -> Callable[..., Awaitable[Any]]:
    module = callable.__module__
    name = callable.__name__

    @functools.wraps(callable)
    async def client_stub(*args: Any, **kwargs: Any) -> Any:
        return await _invoke_server_function_remote(module, name, args, kwargs)

    setattr(client_stub, _BLU_SERVER_FN_ATTR, True)
    return client_stub


def _wrap_server(callable: Callable[..., Any]) -> Callable[..., Awaitable[Any]]:
    if inspect.iscoroutinefunction(callable):
        setattr(callable, _BLU_SERVER_FN_ATTR, True)
        return callable

    @functools.wraps(callable)
    async def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        return await asyncio.to_thread(callable, *args, **kwargs)

    setattr(sync_wrapper, _BLU_SERVER_FN_ATTR, True)
    return sync_wrapper


def server[
    **P, R
](callable: Callable[P, R | Awaitable[R]],) -> Callable[P, Awaitable[R]]:
    """
    Create a server function that can be called from the client.

    .. code-block:: python
        :caption: app/server_functions.py

        from blu import server


        @server
        def read_greeting_from_file(name):
            with open('app/hello.txt', 'r') as f:
                return f.read() + name

    .. code-block:: none
        :caption: app/hello.txt

        Hello,

    .. code-block:: python
        :caption: app/__index__.py

        from blu import client
        from blu.html import div

        __client__ = True


        def __page__():
            return MyClientElement


        @client
        def MyClientElement():
            return div[read_greeting_from_file('George')]

    .. code-block:: html

        <div>Hello, George!</div>

    :param callable: A :class:`Callable <collections.abc.Callable>`
    :return: An asynchronous function that, when called in a client
        environment, runs ``callable`` on the server with the provided
        arguments, and returns the return value of ``callable``.

    When calling the returned function in a client environment, the
    arguments provided must be JSON-serializable and the return value
    must be picklable. Otherwise, the function will be unable to
    complete.

    The function must be defined at the top level of a module in order
    to be accessible client-side.

    .. code-block:: python
        :caption: Wrong!

        class A:

            @server
            def func():
                return 1


    .. code-block:: python
        :caption: Wrong!

        def func_factory():

            @server
            def func():
                return 1

            return func

    .. code-block:: python
        :caption: Right.

        @server
        def func():
            return 1
    """
    if is_client:
        return _wrap_client(callable)
    return _wrap_server(callable)


async def handle_server_function_request(
    receive: Callable[[], Awaitable[dict[str, Any]]],
    send: Callable[[dict[str, Any]], Awaitable[None]],
) -> None:
    body = await _read_http_request_body(receive)
    try:
        data = json.loads(body.decode("utf-8"))
        module_name = data["module"]
        fn_name = data["name"]
        args = data.get("args") or []
        kwargs = data.get("kwargs") or {}
    except (json.JSONDecodeError, KeyError, UnicodeDecodeError) as e:
        await _send_server_function_json(
            send,
            400,
            {"ok": False, "error": f"invalid request"},
        )
        return

    if not _allowed_server_rpc_target(module_name, fn_name):
        await _send_server_function_json(
            send,
            404,
            {"ok": False, "error": "Not Found"},
        )
        return

    try:
        mod = importlib.import_module(module_name)
        fn = getattr(mod, fn_name)
    except (ImportError, AttributeError):
        await _send_server_function_json(
            send,
            404,
            {"ok": False, "error": "Not Found"},
        )
        return

    if not _is_registered_server_function(fn):
        await _send_server_function_json(
            send,
            404,
            {"ok": False, "error": "Not Found"},
        )
        return

    try:
        if inspect.iscoroutinefunction(fn):
            result = await fn(*args, **kwargs)
        else:
            result = await asyncio.to_thread(fn, *args, **kwargs)
    except Exception as e:
        await _send_server_function_json(
            send,
            500,
            {"ok": False, "error": ""},
        )
        return

    pickled = pickle.dumps(result)
    b64 = base64.b64encode(pickled).decode("ascii")
    await _send_server_function_json(
        send,
        200,
        {"ok": True, "result_b64": b64},
    )


async def _read_http_request_body(
    receive: Callable[[], Awaitable[dict[str, Any]]],
) -> bytes:
    body = b""
    while True:
        message = await receive()
        if message["type"] != "http.request":
            continue
        body += message.get("body", b"")
        if not message.get("more_body", False):
            break
    return body


async def _send_server_function_json(
    send: Callable[[dict[str, Any]], Awaitable[None]],
    status: int,
    payload: dict[str, Any],
) -> None:
    raw = json.dumps(payload).encode("utf-8")
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"Content-Type", b"application/json; charset=utf-8"),
            ],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": raw,
            "more_body": False,
        }
    )
