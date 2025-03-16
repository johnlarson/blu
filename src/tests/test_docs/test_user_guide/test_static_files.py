from playwright.async_api import Page, expect
import requests

from tests.utils import prod_cli, prod_server


async def test_basic_example():
    """
    From docs:

    To serve a static file, place it in your app/ directory in the route
    that it should be served from
    """
    async with prod_cli('tests.apps.static_files') as url:
        res = requests.get(url + '/path/to/static/file.txt')
        assert res.text == 'Hello, World!'