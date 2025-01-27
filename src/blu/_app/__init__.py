from collections.abc import AsyncGenerator, AsyncIterable, AsyncIterator, Mapping
from contextlib import asynccontextmanager
from importlib import import_module
from pathlib import Path
import pkgutil
from types import ModuleType, TracebackType
from typing import Optional
from quart import Quart, Response as QuartResponse

from .asgi_app.router import Router
from .asgi_app import call_asgi
from blu._react.types import Node
from blu._utils import asgi


class Blu:
    app_dir: Path
    project_root: Path
    is_dev: bool

    _router: Router

    @property
    def static_dir(self):
        return self.project_root / 'static'

    def __init__(
        self,
        app: str,
        project: Optional[Path | str],
        dev: bool = False,
    ):
        self._router = Router(app)

    async def __call__(
        self,
        scope: asgi.Scope,
        receive: asgi.Receiver,
        send: asgi.Sender,
    ):
        await call_asgi(scope, receive, send)

    async def build(self):
        ...

    @asynccontextmanager
    async def dev(self) -> AsyncGenerator['Blu']:
        ...
    
    


