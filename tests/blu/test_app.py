from contextlib import contextmanager
import importlib
import sys
from types import ModuleType
from pytest import MonkeyPatch
import pytest
import blu
from blu import WrongEnvironmentError, app
from tests.utils import Sender, projects, receive
from blu._app import _get_router  # type: ignore
from blu import _utils


def patch_app(module_name: str):
    module = importlib.import_module(f'tests.apps.{module_name}')
    sys.modules['app'] = module
    _get_router.cache_clear()


async def test_runs_blu_from_app_module(monkeypatch: MonkeyPatch):
    """
    app is an ASGI app that runs the Blu application defined in the
    current Python environment's "app" package.
    """
    patch_app('static_files')
    sender = Sender()
    await app(
        {
            'asgi': {
                'version': '1',
                'spec_version': '2.0',
            },
            'path': '/path/to/static/file.txt',
            'headers': [],
            'type': 'http',
            'http_version': '1.1',
            'method': 'GET',
            'query_string': b'',
        },
        receive,
        sender,
    )
    assert sender.body() == 'Hello, World!'


async def test_raises_WrongEnvironmentError_on_client(monkeypatch: MonkeyPatch):
    """
    Calling app client-side results in a blu.WrongEnvironmentError being
    raised.
    """
    monkeypatch.setattr(_utils, 'is_client', True)
    with pytest.raises(WrongEnvironmentError):
        await app(
            {
                'asgi': {
                    'version': '1',
                    'spec_version': '2.0',
                },
                'path': '/',
                'headers': [],
                'type': 'http',
                'http_version': '1.1',
                'method': 'GET',
                'query_string': b'',
            },
            receive,
            Sender(),
        )
