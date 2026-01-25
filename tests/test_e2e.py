from asyncio import Task, sleep
import asyncio
from collections.abc import AsyncGenerator, Awaitable, Callable, Generator
from typing import cast
import aiohttp
from playwright.async_api import (
    async_playwright, Page, BrowserType, BrowserContext, expect
)
import pytest
import uvicorn

from blu._utils import get_available_port


@pytest.fixture
async def client(patch_app, server: Callable[[], Awaitable[str]]):  # type: ignore
    session: aiohttp.ClientSession | None = None
    try:
        async def ret(app_name: str):
            nonlocal session
            patch_app(app_name)
            session = aiohttp.ClientSession(await server())
            await session.__aenter__()
            return session
        yield ret
    finally:
        if session is not None:
            await session.__aexit__()


@pytest.fixture
async def page(
    patch_app: Callable[[str], None],
    server: Callable[[], Awaitable[str]],
) -> AsyncGenerator[Callable[[str], Awaitable[Page]]]:
    async with async_playwright() as playwright:
        chromium = playwright.chromium
        browser = await chromium.launch(headless=False)
        async def ret(app_name: str) -> Page:
            patch_app(app_name)
            base_url = await server()
            context = await browser.new_context(base_url=base_url)
            return await context.new_page()
        try:
            yield ret
        finally:
            await browser.close()


@pytest.fixture
async def page_old(
    # patch_app: Callable[[str], None],
    web_browser: BrowserType,
    # server: Callable[[], Awaitable[str]],
) -> AsyncGenerator[Callable[[str], Awaitable[Page]]]:
    async with async_playwright() as playwright:
        chromium = playwright.chromium
        browser = await chromium.launch(headless=False)
    async def ret(app_name: str) -> Page:
        # patch_app(app_name)
        # base_url = await server()
        # context = cast(
        #     BrowserContext,
        #     await web_browser.new_context(base_url=base_url),  # type: ignore
        # )
        context = cast(BrowserContext, await web_browser.new_context())
        print('CREATED_CONTEXT!!!!')
        return await context.new_page()
    yield ret


@pytest.fixture
def server() -> Generator[Callable[[], Awaitable[str]]]:
    server_task: Task[None] | None = None
    try:
        async def ret() -> str:
            nonlocal server_task
            port = get_available_port()
            from blu import app
            config = uvicorn.Config(app, port=port)
            server = uvicorn.Server(config)
            server_task = asyncio.create_task(server.serve())
            base_url = f'http://127.0.0.1:{port}'
            async with aiohttp.ClientSession(base_url) as session:
                await _wait_for_server_start(session)
            return base_url
        yield ret
    finally:
        if server_task is not None:
            server_task.cancel()


@pytest.fixture(scope='module')
async def web_browser():
    async with async_playwright() as playwright:
        chromium = playwright.chromium
        yield await chromium.launch(headless=True, slow_mo=50)


async def _wait_for_server_start(session: aiohttp.ClientSession):
    for _ in range(25):
        await asyncio.sleep(.1)
        try:
            async with session.get('/'):
                return
        except aiohttp.ClientConnectorError:
            pass
    raise TimeoutError('Dev server never started.')


async def test_render_nodes(page: Callable[[str], Awaitable[Page]]):
    """Nodes should render as described in the documentation."""
    p = await page('e2e')
    await p.goto('/rendering')
    await sleep(300)
    del_ = p.locator('del')
    await expect(del_).to_have_count(1)
    await expect(del_).to_have_id('my-id')
    await expect(del_).to_have_text('ABCDEF12.0truefalse')


async def test_routing():
    """Requests should be routed as described in the documentation."""
    ...


async def test_is_client():
    """
    blu.is_client should be True client-side and False server-side.
    """
    ...


async def test_wrong_environment_error():
    """
    Trying to use blu.Response or blu.app client-side should raise a
    blu.WrongEnvironmentError.
    """
    ...


async def test_use_effect():
    """blu.use_effect should work as described in the documentation."""
    ...


async def test_use_ref():
    """
    blu.use_ref should store references and be editable as described in
    the documentation.
    """
    ...


async def test_use_state():
    """
    blu.use_state should behave as described in the documentation.
    """
    ...


async def test_use_ref_html_element():
    """
    Passing a Ref as the "ref" prop of an HTML element should result in
    that Ref referencing the HTML element in an effect and during the
    following render.
    """
    ...


async def test_client_side_availability():
    """The blu, js, and pyscript packages are available client-side."""
    ...


async def test_static_files():
    """Static files are accessible as described in the documentation."""
    ...


async def test_client_file_specifier():
    """
    Python files within the app package are available client-side if
    they contain the top-level statement "__client__ = True"; otherwise,
    they are not available client-side.
    """
    ...


async def test_dev_server():
    """
    Running `blu` on the command line causes a dev server to run. The
    output of the command line tells which port it is running on. The
    server runs the blu application described in the app package, and
    the server reloads any time there is a change to Python files in the
    app package.
    """
    ...