from collections.abc import Awaitable, Callable
import importlib
from unittest import mock

from contextlib import contextmanager
from pathlib import Path

import aiohttp
from blu._utils import asgi
from blu import is_client
from blu import _utils
from blu._utils import client as client_utils

if not is_client:
    pass


tests = Path(__file__).parent
projects = tests / "projects"
test_projects = projects

type ClientFixture = Callable[[str], Awaitable[aiohttp.ClientSession]]

type PageFixture = Callable[[str], Awaitable[Page]]


async def receive() -> asgi.ReceiveEvent:
    return {"type": "http.request"}


class Sender(asgi.Sender):
    _events: list[asgi.SendEvent]

    def __init__(self):
        self._events = []

    async def __call__(self, event: asgi.SendEvent):
        self._events.append(event)

    def __next__(self) -> asgi.SendEvent:
        try:
            return self._events.pop(0)
        except IndexError:
            raise Exception("No more response body.")

    def __iter__(self):
        return self

    def body(self) -> str:
        ret_bytes = b""
        for event in self:
            if event["type"] == "http.response.body":
                ret_bytes += event.get("body", b"")
                if not event.get("more_body", False):
                    break
        return ret_bytes.decode("utf-8")


async def asgi_get(path: str) -> Sender:
    from blu import app

    if "?" in path:
        path, query_str = path.split("?")
        query = query_str.encode("utf-8")
    else:
        query = b""
    sender = Sender()
    await app(
        {
            "asgi": {
                "version": "1",
                "spec_version": "2.0",
            },
            "path": path,
            "headers": [],
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "query_string": query,
        },
        receive,
        sender,
    )
    return sender


@contextmanager
def reload_is_client(system: str):
    with mock.patch("platform.system", return_value=system):
        _reload_is_client()
        yield
    _reload_is_client()


def _reload_is_client():
    import blu._app
    import blu._server_functions

    importlib.reload(client_utils)
    importlib.reload(_utils)
    importlib.reload(blu._server_functions)
    importlib.reload(blu._app)
    importlib.reload(blu)
