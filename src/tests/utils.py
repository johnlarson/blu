import asyncio
from collections.abc import AsyncGenerator, Generator, Iterable, Iterator, Mapping
from contextlib import asynccontextmanager, contextmanager
from importlib import import_module
import os
from pathlib import Path
import re
from subprocess import PIPE, Popen
import sys
from tempfile import TemporaryDirectory
from threading import Thread
from typing import Any, AnyStr, Literal, Optional, TypedDict, cast
from bs4 import BeautifulSoup
import uvicorn
from blu._app import Blu
from blu._utils import asgi, get_available_port, watch_dev_app
from blu._utils import json


tests = Path(__file__).parent
projects = tests / 'projects'
test_projects = projects


@contextmanager
def temp_dir() -> Generator[Path]:
    with TemporaryDirectory() as tempdir:
        yield Path(tempdir)


@asynccontextmanager
async def dev_app(app_module: str) -> AsyncGenerator[Blu]:
    with temp_dir() as project_dir:
        app = Blu(app_module, project_dir)
        async with app.dev() as dev_app:
            yield dev_app


@asynccontextmanager
async def prod_app(app_module: str) -> AsyncGenerator[Blu]:
    with temp_dir() as project_dir:
        app = Blu(app_module, project_dir)
        await app.build()
        yield app


@asynccontextmanager
async def dev_server(app_module: str) -> AsyncGenerator[str]:
    with temp_dir() as project_dir:
        async with Blu(app_module, project_dir).dev() as app:
            async with _test_serve(app) as url:
                yield url


@asynccontextmanager
async def prod_server(app_module: str) -> AsyncGenerator[str]:
    with temp_dir() as project_dir:
        app = Blu(app_module, project_dir)
        async with _test_serve(app) as url:
            yield url


@asynccontextmanager
async def _test_serve(app: Blu) -> AsyncGenerator[str]:
    port = get_available_port()
    config = uvicorn.Config(app, port=port)
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve())
    yield f'http://localhost{port}'
    await task


async def receive() -> asgi.ReceiveEvent:
    return {'type': 'http.request'}


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
            raise Exception('No more response body.')

    def __iter__(self):
        return self
    
    def body(self) -> str:
        ret_bytes = b''
        for event in self:
            if event['type'] == 'http.response.body':
                ret_bytes += event.get('body', b'')
                if not event.get('more_body', False):
                    break
        return ret_bytes.decode('utf-8')



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


async def react_data(body: str) -> ReactDataNode:
    soup = BeautifulSoup(body)
    react_data_tag = soup.select('script[type="react-data"]')[0]
    react_data_text = react_data_tag.string
    assert react_data_text is not None
    react_data_not_validated = await json.loads(react_data_text)
    return validate_react_data(react_data_not_validated)


def validate_react_data(json_data: json.JsonData) -> ReactDataNode:
    if json_data is None:
        return json_data
    if isinstance(json_data, (bool, int, float, str)):
        return json_data
    return assert_react_html_data(json_data)


def assert_react_html_data(json_data: json.JsonData) -> HTMLReactData:
    if not isinstance(json_data, Mapping):
        raise ValidationError
    try:
        if json_data['type'] != 'native_element':
            raise ValidationError
    except KeyError:
        raise ValidationError
    try:
        if not isinstance(json_data['tagname'], str):
            raise ValidationError
    except KeyError:
        raise ValidationError
    try:
        attrs = cast(Any, json_data['props'])
    except KeyError:
        raise ValidationError
    if not isinstance(attrs, Mapping):
        raise ValidationError
    for k in cast(Mapping[Any, Any], attrs):
        v = cast(Any, attrs[k])
        if not isinstance(k, str):
            raise ValidationError
        if not isinstance(v, str):
            raise ValidationError
    try:
        children = cast(Any, json_data['children'])
    except KeyError:
        raise ValidationError
    if not isinstance(children, Iterable):
        raise ValidationError
    for child in cast(Iterable[Any], children):
        validate_react_data(child)
    return cast(HTMLReactData, json_data)


def mapping_get(mapping: Mapping[Any, Any], key: Any, default: Any = None) -> Any:
    try:
        return mapping[key]
    except KeyError:
        return default


class ValidationError(Exception):
    pass
