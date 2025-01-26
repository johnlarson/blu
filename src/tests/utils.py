import asyncio
from collections.abc import AsyncGenerator, Callable, Generator, Iterable, Mapping
from contextlib import asynccontextmanager, contextmanager
from importlib import import_module
import os
from pathlib import Path
import re
from subprocess import PIPE, Popen
import sys
from tempfile import TemporaryDirectory
from threading import Thread
from typing import Literal, Optional, TypedDict, cast

import uvicorn
from blu._app import Blu
from blu._utils import asgi


tests = Path(__file__).parent
projects = tests / 'projects'


@contextmanager
def temp_dir() -> Generator[Path]:
    with TemporaryDirectory() as tempdir:
        yield Path(tempdir)


@asynccontextmanager
async def dev_app(app_module: str) -> AsyncGenerator[Blu]:
    app_def = import_module(app_module)
    with temp_dir() as project_dir:
        app = Blu(app_def, project_dir, dev=True)
        async with _watch_dev_app(app):
            yield app


@asynccontextmanager
async def prod_app(app_module: str) -> AsyncGenerator[Blu]:
    app_def = import_module(app_module)
    with temp_dir() as project_dir:
        app = Blu(app_def, project_dir)
        await app.build()
        yield app


@asynccontextmanager
async def dev_server(app_module: str) -> AsyncGenerator[str]:
    app_def = import_module(app_module)
    with temp_dir() as project_dir:
        async with Blu(app_def, project_dir).dev() as url:
            yield url


@asynccontextmanager
async def prod_server(app_module: str) -> AsyncGenerator[str]:
    app_def = import_module(app_module)
    with temp_dir() as project_dir:
        app = Blu(app_def, project_dir)
        async with _serve_prod(app) as url:
            yield url


@asynccontextmanager
async def _serve_prod(app: Blu) -> AsyncGenerator[str]:
    port = 5000
    config = uvicorn.Config(app, port=port)
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve())
    yield f'http://localhost{port}'
    await task


async def receive() -> asgi.ReceiveEvent:
    return {'type': 'http.request'}


class Sender(asgi.Sender):

    def __init__(self):
        ...

    async def __call__(self, event: asgi.SendEvent):
        ...

    def __next__(self):
        ...

    def body(self) -> str:
        ...

@contextmanager
def background(
    command: list[str],
    cwd: Optional[str | Path] = None,
    env: dict[str, str] = {},
) -> Generator[Popen[str], None, None]:
    with Popen(
        command,
        cwd=cwd,
        stdout=PIPE,
        stderr=PIPE,
        env={**os.environ, 'PYTHONPATH': ':'.join(sys.path), **env},
        text=True,
    ) as proc:
        try:
            yield proc
        finally:
            proc.kill()

\
def get_app_url(proc: Popen[str]) -> str:
    ret_container: list[None | int] = [None]
    thread = Thread(
        target=_get_app_url_target,
        args=[proc, ret_container],
    )
    thread.start()
    thread.join()
    ret = ret_container[0]
    if isinstance(ret, str):
        return ret
    raise Exception('Unable to set port number.')


def _get_app_url_target(
    proc: Popen[str], ret_container: list[int | None]
) -> None:
    for line in cast(Iterable[str], proc.stderr):
        re_match = re.search(r'(http://127\.0\.0\.1:\d+)', line)
        if re_match is not None:
            ret_container[0] = int(re_match[1])
            return
    raise Exception('Process completed without specifying port in stderr.')


class HTMLReactData(TypedDict):
    type: Literal['html']
    tagname: str
    attrs: Mapping[str, str]
    children: Iterable['ReactDataNode']


type ReactDataNode = None | bool | int | float | str | HTMLReactData


def react_data(body: str) -> ReactDataNode:
    ...


@asynccontextmanager
async def _watch_dev_app(app: Blu) -> AsyncGenerator[None]:
    ...