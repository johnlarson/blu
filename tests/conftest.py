from asyncio import Task
import asyncio
from collections.abc import AsyncGenerator, Awaitable, Callable
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
from typing import Generator

import aiohttp
from playwright.async_api import async_playwright, Page
import pytest
import uvicorn
from blu._app import _get_app_def, _get_router  # type: ignore
from blu._settings import settings
from blu._utils import get_available_port

HEADLESS = True


@pytest.fixture
async def page(
    patch_app: Callable[[str], None],
    server: Callable[[], Awaitable[str]],
) -> AsyncGenerator[Callable[[str], Awaitable[Page]]]:
    async with async_playwright() as playwright:
        chromium = playwright.chromium
        browser = await chromium.launch(headless=HEADLESS)

        async def ret(app_name: str) -> Page:
            patch_app(app_name)
            base_url = await server()
            context = await browser.new_context(base_url=base_url)
            page = await context.new_page()
            page.base_url = base_url  # type: ignore
            return page

        try:
            yield ret
        finally:
            await browser.close()


@pytest.fixture(scope="module")
async def web_browser():
    async with async_playwright() as playwright:
        chromium = playwright.chromium
        yield await chromium.launch(headless=HEADLESS, slow_mo=50)


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
            await session.__aexit__(None, None, None)


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
            base_url = f"http://127.0.0.1:{port}"
            async with aiohttp.ClientSession(base_url) as session:
                await _wait_for_server_start(session)
            return base_url

        yield ret
    finally:
        if server_task is not None:
            try:
                server_task.cancel()
            except RuntimeError:
                pass


async def _wait_for_server_start(session: aiohttp.ClientSession):
    for _ in range(25):
        await asyncio.sleep(0.1)
        try:
            async with session.get("/"):
                return
        except aiohttp.ClientConnectorError:
            pass
    raise TimeoutError("Dev server never started.")


TESTS_DIR = Path(__file__).parent


@pytest.fixture
def patch_app(patch_project_dir):  # type: ignore
    with TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)

        def handler(app_name: str):
            for path in temp_dir.iterdir():
                shutil.rmtree(path)
            src_path = TESTS_DIR / "apps" / app_name
            ln_path = temp_dir / "app"
            ln_path.symlink_to(src_path)
            patch_project_dir(temp_dir)

        yield handler


@pytest.fixture
def patch_project(patch_project_dir):  # type: ignore
    def handler(project_name: str):
        patch_project_dir(TESTS_DIR / "projects" / project_name)

    yield handler


@pytest.fixture
def patch_project_dir(monkeypatch: pytest.MonkeyPatch):
    def handler(path: Path):
        to_delete = [x for x in sys.modules if x == "app" or x.startswith("app.")]
        for name in to_delete:
            del sys.modules[name]
        monkeypatch.syspath_prepend(path)  # type: ignore
        monkeypatch.chdir(path)
        settings.cache_clear()
        _get_app_def.cache_clear()
        _get_router.cache_clear()

    yield handler
