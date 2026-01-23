from collections.abc import AsyncGenerator
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
from aiohttp import ClientSession
import aiohttp
from playwright.async_api import async_playwright, Page
import pytest

from blu._app import _get_app_def, _get_router  # type: ignore
from blu._settings import settings


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


TESTS_DIR = Path(__file__).parent


@pytest.fixture
def patch_app(patch_project_dir):  # type: ignore
    with TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        def handler(app_name: str):
            for path in temp_dir.iterdir():
                shutil.rmtree(path)
            src_path = TESTS_DIR / 'apps' / app_name
            ln_path = temp_dir / 'app'
            ln_path.symlink_to(src_path)
            patch_project_dir(temp_dir)
        yield handler
        

@pytest.fixture
def patch_project(patch_project_dir):  # type: ignore
    def handler(project_name: str):
        patch_project_dir(TESTS_DIR / 'projects' / project_name)
    yield handler


@pytest.fixture
def patch_project_dir(monkeypatch: pytest.MonkeyPatch):
    def handler(path: Path):
        to_delete = [
            x for x in sys.modules if x == 'app' or x.startswith('app.')
        ]
        for name in to_delete:
            del sys.modules[name]
        monkeypatch.syspath_prepend(path)  # type: ignore
        settings.cache_clear()
        _get_app_def.cache_clear()
        _get_router.cache_clear()
    yield handler
