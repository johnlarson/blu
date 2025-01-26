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
        dev: bool = False,
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
    
    


