import asyncio
import importlib
from blu._settings import settings
from blu._app import _get_app_def, _get_router
from blu._nodes import ClientElement, HTMLElement, Key, Node
from blu._utils.typing import AsyncGenerator, Generator, Iterable, Mapping
from contextlib import asynccontextmanager, contextmanager
from importlib import import_module
import os
from pathlib import Path
import re
from subprocess import PIPE, Popen
import sys
from tempfile import TemporaryDirectory
from threading import Thread
from typing import Any, Literal, Optional, TypedDict, cast
from bs4 import BeautifulSoup
import uvicorn
from blu._utils import asgi, get_available_port
from blu._utils import json
from blu import is_client

if not is_client:
    import shutil
    import socket


tests = Path(__file__).parent
projects = tests / 'projects'
test_projects = projects


@contextmanager
def temp_dir() -> Generator[Path]:
    with TemporaryDirectory() as tempdir:
        yield Path(tempdir)


class Blu:
    pass


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
    async with prod_app(app_module) as app:
        async with _test_serve(app) as url:
            yield url


@asynccontextmanager
async def dev_cli(app_module: str) -> AsyncGenerator[str]:
    async with copy_app_dir(app_module) as temp_dir:

        with background(['blu', 'dev'], temp_dir) as proc:
            yield get_app_url(proc)


@asynccontextmanager
async def prod_cli(app_module: str, build: bool = True) -> AsyncGenerator[str]:
    port = get_available_port()
    async with copy_app_dir(app_module) as temp_dir:
        if build:
            await run(['blu', 'build'], temp_dir)
        with background(
            ['uvicorn', 'blu:app', '--port', str(port)],
            temp_dir,
        ) as proc:
            yield get_app_url(proc)


@asynccontextmanager
async def copy_app_dir(app_module: str) -> AsyncGenerator[Path]:
    module = import_module(app_module)
    assert hasattr(module, '__path__')
    src_dir = Path(getattr(module, '__path__')[0])
    with TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        shutil.copytree(src_dir, temp_dir / 'app')  # type: ignore
        yield temp_dir


@asynccontextmanager
async def _test_serve_old(app: Blu) -> AsyncGenerator[str]:
    host = '127.0.0.1'
    port = get_available_port()
    config = uvicorn.Config(app, host, port)
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve())
    yield f'http://{host}:{port}'
    await task


@asynccontextmanager
async def _test_serve(app: asgi.App,) -> AsyncGenerator[str]:
    server_task: Optional[asyncio.Task[Any]] = None
    try:
        port = get_available_port()
        host = '127.0.0.1'
        location = f'{host}:{port}'
        config = uvicorn.Config(app, host, port)
        server = uvicorn.Server(config)
        server_task = asyncio.create_task(server.serve())
        while True:
            if _ping_server(host, port):
                break
            else:
                await asyncio.sleep(.1)
        yield f'http://{location}'
    except Exception as exc:
        if server_task is not None:
            server_task.cancel()
            # await server_task
            await asyncio.sleep(0)
            raise exc
    else:
        assert server_task is not None
        server_task.cancel()
        await server.shutdown()
        # await server_task
        await asyncio.sleep(0)


def _ping_server(address: str, port: int, timeout: int = 1):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # type: ignore
    s.settimeout(timeout)
    try:
        s.connect((address, port))
    except OSError:
        return False
    else:
        s.close()
        return True


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


async def asgi_get(app: asgi.App, path: str) -> Sender:
    if '?' in path:
        path, query_str = path.split('?')
        query = query_str.encode('utf-8')
    else:
        query = b''
    sender = Sender()
    await app(
        {
            'asgi': {
                'version': '1',
                'spec_version': '2.0',
            },
            'path': path,
            'headers': [],
            'type': 'http',
            'http_version': '1.1',
            'method': 'GET',
            'query_string': query,
        },
        receive,
        sender,
    )
    return sender


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


def run_old(
    command: list[str],
    cwd: Optional[str | Path] = None,
    env: dict[str, str] = {},
) -> Popen[str]:
    with background(command, cwd, env) as proc:
        pass
    return proc


async def run(
    command: list[str],
    cwd: Optional[str | Path] = None,
    env: dict[str, str] = {},
) -> tuple[Iterable[str], Iterable[str]]:
    proc = await asyncio.create_subprocess_exec(
        *command,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env={**os.environ, 'PYTHONPATH': ':'.join(sys.path), **env},
    )
    stdout, stderr = await proc.communicate()
    return stdout.decode(), stderr.decode()



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
    proc: Popen[str], ret_container: list[str | None]
) -> None:
    for line in cast(Iterable[str], proc.stderr):
        re_match = re.search(r'(http://127\.0\.0\.1:\d+)', line)
        if re_match is not None:
            ret_container[0] = re_match[1]
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


def renders_as(input: Node, rendered: Node) -> bool:
    return node_eq(render(input), rendered)


def render(node: Node) -> Node:
    return render_page_node(node)


def node_eq(n1: Node, n2: Node) -> bool:
    if type(n1) != type(n2):
        return False
    if isinstance(n1, ClientElement):
        return _client_element_eq(n1, n2)
    if isinstance(n1, HTMLElement):
        return _html_element_eq(n1, n2)
    if isinstance(n1, Key):
        return _key_eq(n1, n2)
    if isinstance(n1, Iterable) and not isinstance(n1, str):
        return _iterable_eq(n1, n2)
    return n1 == n2
    
def _client_element_eq(e1: ClientElement, e2: ClientElement) -> bool:
    if e1._renderer != e2._renderer:
        return False
    if e1._args != e2._args:
        return False
    if e1._kwargs != e2._kwargs:
        return False
    return _children_eq(e1, e2)


def _html_element_eq(e1: HTMLElement, e2: HTMLElement) -> bool:
    if e1._tagname != e2._tagname:
        return False
    if e1._attrs != e2._attrs:
        return False
    return _children_eq(e1, e2)


def _children_eq(
    e1: ClientElement | HTMLElement | Key,
    e2: ClientElement | HTMLElement | Key,
) -> bool:
    return _iterable_eq(e1._children, e2._children)


def _key_eq(e1: Key, e2: Key) -> bool:
    if e1._key != e2._key:
        return False
    return _children_eq(e1, e2)


def _iterable_eq(i1: Iterable, i2: Iterable) -> bool:
    if len(i1) != len(i2):
        return False
    return all(
        node_eq(x1, i2[i])
        for i, x1 in enumerate(i1)
    )


def patch_app(module_name: str):
    module = importlib.import_module(f'tests.apps.{module_name}')
    sys.modules['app'] = module
    _get_app_def.cache_clear()
    _get_router.cache_clear()
    settings.cache_clear()