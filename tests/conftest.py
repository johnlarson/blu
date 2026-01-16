from collections.abc import AsyncGenerator
from aiohttp import ClientSession
import aiohttp
from playwright.async_api import async_playwright, Page
import pytest


@pytest.fixture
async def page() -> AsyncGenerator[Page, None]:
    async with async_playwright() as playwright:
        chromium = playwright.chromium
        headless = False
        # headless = True
        browser = await chromium.launch(headless=headless)
        print('START')
        yield await browser.new_page()
        print('END')
        pass


@pytest.fixture
async def client() -> AsyncGenerator[ClientSession]:
    async with aiohttp.ClientSession() as session:
        yield session