from asyncio import Task
import asyncio
from datetime import datetime
from operator import index
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent
from threading import Thread
from unittest.mock import patch
import aiohttp
import pytest

from blu._utils import get_available_port
from blu._cli import main
from blu._utils.asyncio import cpu_bound


@pytest.fixture
async def dev_server_client():  # type: ignore
    port = get_available_port()
    with patch('blu._cli.get_available_port', return_value=port):
        async_main = cpu_bound(main)
        task = Task(async_main())
        base_url = f'http://localhost:{port}'
        async with aiohttp.ClientSession(base_url) as session:
            start_time = datetime.now()
            while True:
                await asyncio.sleep(.2)
                if (datetime.now() - start_time).seconds > 5:
                    task.cancel()
                    raise TimeoutError('Dev server never started.')
                try:
                    async with session.get('/'):
                        pass
                except Exception:
                    pass
                else:
                    break
            yield session
        task.cancel()
            

async def test_dev_server(dev_server_client: ClientSession, patch_app):  # type: ignore
    """
    When a `blu` is run, a dev server starts up that serves the app on a
    port that is given by the output to `blu`.
    """
    patch_app('static_files')
    async with dev_server_client.get('/path/to/static/file.txt') as response:
        assert await response.text() == 'Hello, World!'


async def test_reload_on_change(patch_project_dir, dev_server_client: ClientSession):  # type: ignore
    """The dev server reloads when a Python file is changed."""
    with TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        patch_project_dir(temp_dir)
        app_dir = temp_dir / 'app'
        app_dir.mkdir()
        async with dev_server_client.get('/') as response:
            assert response.status == 404
        start_time = datetime.now()
        index_file_path = app_dir / '__index__.py'
        index_file_path.write_text('def __page__(): return "Hello, World!"')
        while True:
            asyncio.sleep(.5)
            assert (datetime.now() - start_time).seconds < 5
            async with dev_server_client.get('/') as response:
                if response.status == 200:
                    return