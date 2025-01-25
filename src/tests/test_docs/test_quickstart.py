from collections.abc import AsyncGenerator

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, expect
import pytest

from tests.utils import Sender, background, dev_app, dev_server, get_app_url, projects, react_data, receive


@pytest.fixture
async def page() -> AsyncGenerator[Page, None]:
    async with async_playwright() as playwright:
        chromium = playwright.chromium
        headless = False
        headless = True
        browser = await chromium.launch(headless=headless)
        print('START')
        yield await browser.new_page()
        print('END')
        pass


async def test_quickstart(page: Page):
    """The example in the quickstart guide."""
    
    with background(['blu', 'dev'], projects / 'quickstart') as proc:
        url = get_app_url(proc)
        await page.goto(url)
        html = page.locator('html')
        await html.wait_for(state='attached')
        await expect(html.locator('> head nth-child(1)')).to_be_attached()
        body = html.locator('> body nth-child(2)')
        await expect(body).to_have_text('Hello World!')


async def test_quickstart__server(page: Page):
    """The example in the quickstart guide (Server)."""

    async with dev_server('testing.apps.quickstart') as url:
        await page.goto(url)
        html = page.locator('html')
        await html.wait_for(state='attached')
        await expect(html.locator('> head nth-child(1)')).to_be_attached()
        body = html.locator('> body nth-child(2)')
        await expect(body).to_have_text('Hello World!')


async def test_quickstart__app():
    send = Sender()
    async with dev_app('testing.apps.quickstart') as app:
        await app(
            {
                'type': 'http',
                'http_version': '2',
                'method': 'GET',
                'query_string': b'',
                'asgi': {'version': '1.0'},
                'path': '/',
                'headers': [],
            },
            receive,
            send,
        )
    assert react_data(send.body()) == {
        'type': 'html',
        'tagname': 'html',
        'attrs': {},
        'children': [
            {
                'type': 'html',
                'tagname': 'head',
                'attrs': {},
                'children': [],
            },
            {
                'type': 'html',
                'tagname': 'body',
                'attrs': {},
                'children': [
                    'Hello World!',
                ],
            },
        ],
    }


