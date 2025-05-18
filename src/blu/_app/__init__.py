from blu._utils.typing import AsyncGenerator
from contextlib import asynccontextmanager
import functools
from importlib import import_module
from pathlib import Path
import pkgutil
from types import ModuleType, TracebackType
from blu._utils.typing import Optional

from blu._app._build import build
from blu._app._dev import watch_build
# from quart import Quart, Response as QuartResponse

from .asgi_app.router import Router
from .asgi_app import ASGIApp
from blu._react.types import Node
from blu._utils import asgi


class Blu:
    project_root: Path
    is_dev: bool

    _asgi_app: asgi.App
    _app_import_path: str

    @property
    def static_dir(self) -> Path:
        return self.project_root / 'static'

    @property
    def build_dir(self) -> Path:
        return self.project_root / '.build'

    @property
    @functools.cache
    def app_dir(self) -> Path:
        app_module = import_module(self._app_import_path)
        return Path(app_module.__path__[0])

    def __init__(
        self,
        app: str,
        project: Optional[Path | str],
        dev: bool = False,
    ):
        if project is not None:
            project = Path(project)
            self.project_root = project
        self._asgi_app = ASGIApp(app, self.static_dir, project)
        self._app_import_path = app

    async def __call__(
        self,
        scope: asgi.Scope,
        receive: asgi.Receiver,
        send: asgi.Sender,
    ):
        await self._asgi_app(scope, receive, send)

    async def build(self):
        await build(self.app_dir, self.static_dir, self.build_dir)

    @asynccontextmanager
    async def dev(self) -> AsyncGenerator['Blu']:
        async with watch_build(self.app_dir, self.static_dir, self.build_dir):
            yield Blu(self._app_import_path, self.project_root, dev=True)
    
    


