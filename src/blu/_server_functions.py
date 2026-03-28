import ast
import asyncio
import base64
import functools
import importlib
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

    Only absolute imports are considered (``level == 0``). ``from blu import
    server`` or ``from blu.<submodule> import server`` binds the
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
            if mod is None or (mod != "blu" and not mod.startswith("blu.")):
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


_server_function_registry: dict[tuple[str, str], Callable[..., Any]] | None = None


def _rpc_key_well_formed(module_name: str, fn_name: str) -> bool:
    if not fn_name.isidentifier():
        return False
    if not module_name.startswith("app.") or module_name == "app":
        return False
    rest = module_name[4:]
    if not rest:
        return False
    return all(p.isidentifier() for p in rest.split("."))


def _app_py_path_to_module_name(app_root: Path, path: Path) -> str:
    rel = path.relative_to(app_root)
    parts = rel.parts
    if parts[-1] == "__init__.py":
        pkg_parts = parts[:-1]
    elif parts[-1].endswith(".py"):
        pkg_parts = (*parts[:-1], parts[-1][:-3])
    else:
        return ""
    if not pkg_parts:
        return "app"
    return "app." + ".".join(pkg_parts)


def _collect_app_module_paths() -> dict[str, Path]:
    import app

    spec = app.__spec__
    if spec is None or not spec.submodule_search_locations:
        return {}
    seen: dict[str, Path] = {}
    for root_str in spec.submodule_search_locations:
        root = Path(root_str)
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            mod_name = _app_py_path_to_module_name(root, path)
            if mod_name and mod_name not in seen:
                seen[mod_name] = path
    return seen


def _discover_server_function_names_from_source(source: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    blu_pkg, server_dec = collect_blu_server_import_bindings(tree.body)
    names: list[str] = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if any(
            decorator_is_server(d, blu_pkg, server_dec) for d in node.decorator_list
        ):
            names.append(node.name)
    return names


def _build_server_function_registry() -> dict[tuple[str, str], Callable[..., Any]]:
    reg: dict[tuple[str, str], Callable[..., Any]] = {}
    for module_name, file_path in _collect_app_module_paths().items():
        try:
            source = file_path.read_text(encoding="utf-8")
        except OSError:
            continue
        fn_names = _discover_server_function_names_from_source(source)
        if not fn_names:
            continue
        try:
            mod = importlib.import_module(module_name)
        except ImportError:
            continue
        for name in fn_names:
            fn = getattr(mod, name, None)
            if fn is not None and _is_registered_server_function(fn):
                reg[(module_name, name)] = fn
    return reg


def refresh_server_function_registry() -> None:
    global _server_function_registry
    _server_function_registry = _build_server_function_registry()


def _ensure_server_function_registry() -> None:
    global _server_function_registry
    if _server_function_registry is None:
        refresh_server_function_registry()


def lookup_server_function(module_name: str, fn_name: str) -> Callable[..., Any] | None:
    """
    Return the registered server callable for ``(module_name, fn_name)`` if any.
    Lazily builds the registry when lifespan has not run (e.g. minimal ASGI hosts).
    """
    _ensure_server_function_registry()
    assert _server_function_registry is not None
    if not _rpc_key_well_formed(module_name, fn_name):
        return None
    return _server_function_registry.get((module_name, fn_name))


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

    fn = lookup_server_function(module_name, fn_name)
    if fn is None:
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
