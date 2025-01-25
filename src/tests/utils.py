from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from types import ModuleType
from blu._app import Blu


tests = Path(__file__).parent
test_apps = tests / 'apps'
test_projects = tests / 'projects'


@asynccontextmanager
async def dev_app(app_def: ModuleType) -> AsyncGenerator[Blu]:
    ...


@asynccontextmanager
async def prod_app(app_def: ModuleType) -> AsyncGenerator[Blu]:
    ...


@asynccontextmanager
async def dev_server(app_def: ModuleType) -> AsyncGenerator[str]:
    ...


@asynccontextmanager
async def prod_server(app_def: ModuleType) -> AsyncGenerator[str]:
    ...