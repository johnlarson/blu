from asyncio import CancelledError, Task
import asyncio
import contextlib
from datetime import datetime
from operator import index
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent
from threading import Thread
from unittest.mock import patch
import aiohttp
from aiohttp import ClientSession
import pytest

from blu._utils import get_available_port
from blu._cli import cli, _run_server
from blu._utils.asyncio import cpu_bound


@pytest.fixture
async def dev_server_client():  # type: ignore
    async with get_dev_server_client() as client:
        yield client

@contextlib.asynccontextmanager
async def get_dev_server_client():
    port = get_available_port()
    with patch('blu._cli.get_available_port', return_value=port):
        # task = Task(_run_server())
        proc = _run_server()
        base_url = f'http://127.0.0.1:{port}'
        async with aiohttp.ClientSession(base_url) as session:
            # await asyncio.sleep(5)
            for _ in range(25):
                await asyncio.sleep(.1)
                try:
                    async with session.get('/'):
                        pass
                    yield session
                    proc.kill()
                    # task.cancel()
                    return
                except aiohttp.ClientConnectorError:
                    pass
        # task.cancel()
        proc.kill()
        raise TimeoutError('Dev server never started.')
            

async def test_dev_server(patch_app):  # type: ignore
    """
    When a `blu` is run, a dev server starts up that serves the app on a
    port that is given by the output to `blu`.
    """
    patch_app('static_files')
    async with get_dev_server_client() as dev_server_client:
        url_path = '/path/to/static/file.txt'
        async with dev_server_client.get(url_path) as response:
            assert await response.text() == 'Hello, World!'
