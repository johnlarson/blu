from collections.abc import AsyncGenerator, Generator, Iterable, Mapping
from contextlib import asynccontextmanager, contextmanager
from importlib import import_module
import os
from pathlib import Path
import re
from subprocess import PIPE, Popen
import sys
from threading import Thread
from types import ModuleType
from typing import Literal, Optional, TypedDict, cast
from blu._app import Blu
from blu._utils import asgi


tests = Path(__file__).parent
projects = tests / 'projects'


def apps(name: str) -> ModuleType:
    return import_module(name, 'tests.apps')


@asynccontextmanager
async def dev_app(app_module: str) -> AsyncGenerator[Blu]:
    ...


@asynccontextmanager
async def prod_app(app_module: str) -> AsyncGenerator[Blu]:
    ...


@asynccontextmanager
async def dev_server(app_module: str) -> AsyncGenerator[str]:
    ...


@asynccontextmanager
async def prod_server(app_module: str) -> AsyncGenerator[str]:
    ...


async def receive() -> asgi.ReceiveEvent:
    ...


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