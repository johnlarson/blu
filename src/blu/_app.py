from collections.abc import AsyncGenerator, AsyncIterable, AsyncIterator, Mapping
from contextlib import asynccontextmanager
from importlib import import_module
from pathlib import Path
import pkgutil
from types import ModuleType, TracebackType
from typing import Optional
from quart import Quart, Response as QuartResponse

from blu._react.types import Node
from blu._utils import asgi


class Blu:
    app_dir: Path
    project_root: Path
    is_dev: bool

    @property
    def static_dir(self):
        ...

    @property
    def build_dir(self):
        ...

    def __init__(
        self,
        app: ModuleType,
        project: Optional[Path | str],
        debug: bool = False,
    ):
        ...

    async def __call__(
        self,
        scope: asgi.Scope,
        receive: asgi.Receiver,
        send: asgi.Sender,
    ):
        ...

    async def build(self):
        ...

    @asynccontextmanager
    async def dev(self) -> AsyncGenerator[str]:
        ...
    
    


class Response(QuartResponse):
    children: Node

    def __init__(
        self,
        children: Node,
        status: Optional[int] = None,
        headers: Mapping[str, str] = {},
    ):
        super().__init__(None, status, Headers(headers))  # type: ignore
        self.children = children


class ReactResponseBody:
    _children: Node

    def __init__(self, children: Node):
        self._children = children
    
    async def __aenter__(self) -> AsyncIterable[AsyncIterator[bytes]]:
        yield get_rendered_bytes(self._children)

    async def __aexit__(
        self,
        exc_type: type,
        exc_value: BaseException,
        tb: TracebackType,
    ):
        pass


async def get_rendered_bytes(node: Node) -> AsyncIterator[bytes]:
    rendered = render_react(node)
    yield rendered.encode('utf-8')


def render_react(node: Node) -> str:
    ...