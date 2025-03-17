from aiohttp import ClientSession as Client
from playwright.async_api import Page, expect
import requests

from tests.utils import prod_cli, prod_server


async def test_basic_example(client: Client):
    """
    From docs:

    To serve a static file, place it in your app/ directory in the route
    that it should be served from
    """
    async with prod_cli('tests.apps.static_files') as url:
        res = await client.get(url + '/path/to/static/file.txt')
        assert await res.text() == 'Hello, World!'


async def test_basic_example__debug(client: Client):
    """
    From docs:

    To serve a static file, place it in your app/ directory in the route
    that it should be served from

    (debuggable)
    """
    async with prod_server('tests.apps.static_files') as url:
        res = await client.get(url + '/path/to/static/file.txt')
        assert await res.text() == 'Hello, World!'