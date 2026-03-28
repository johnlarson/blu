import asyncio
import base64
import functools
import importlib
import inspect
import json
import pickle
from collections.abc import Awaitable, Callable
from typing import Any

from blu._utils.client import is_client

_BLU_SERVER_FN_ATTR = "_blu_is_server_function"


def _is_registered_server_function(fn: Any) -> bool:
    return getattr(fn, _BLU_SERVER_FN_ATTR, False)


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
            {"ok": False, "error": f"invalid request: {e}"},
        )
        return

    try:
        mod = importlib.import_module(module_name)
        fn = getattr(mod, fn_name)
    except (ImportError, AttributeError) as e:
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
