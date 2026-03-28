from asyncio import Task, sleep
import asyncio
from collections.abc import AsyncGenerator, Awaitable, Callable, Generator
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import SpooledTemporaryFile, TemporaryDirectory
import time
from typing import cast
from zipfile import ZipFile
import aiohttp
from playwright.async_api import (
    async_playwright,
    Page,
    BrowserType,
    BrowserContext,
    expect,
)
import pytest
import uvicorn
import re

from blu import is_client
from blu._utils import get_available_port
from tests.utils import ClientFixture, PageFixture

pytestmark = pytest.mark.slow


async def test_render_nodes(page: Callable[[str], Awaitable[Page]]):
    """Nodes should render as described in the documentation."""
    p = await page("e2e")
    await p.goto("/rendering")
    del_ = p.locator("del")
    await expect(del_).to_have_count(1, timeout=10_000)
    await expect(del_).to_have_id("my-id")
    await expect(del_).to_have_text("Hello, World!ABCDEF12.0TrueFalseYZ")


async def test_routing(page: PageFixture):
    """Requests should be routed as described in the documentation."""
    p = await page("e2e")
    route = p.locator("#route")
    await p.goto("/routing/1?q=2")
    await expect(route).to_have_text("/routing/_a_ (1, 2)")
    await p.goto("/routing/1/2/3/4")
    await expect(route).to_have_text("/routing/_a_/... (1, 2/3/4)")
    await p.goto("/routing/1/static")
    await expect(route).to_have_text("/routing/_a_/static (1)")
    await p.goto("/routing/1/2")
    await expect(route).to_have_text("/routing/_a_/_b_ (1, 2)")


async def test_is_client(page: PageFixture):
    """
    blu.is_client should be True client-side and False server-side.
    """
    assert not is_client
    p = await page("e2e")
    await p.goto("/is_client")
    await expect(p.locator("#is_client")).to_have_text("True", timeout=10_000)


async def test_wrong_environment_error(page: PageFixture):
    """
    Trying to use blu.Response or blu.app client-side should raise a
    blu.WrongEnvironmentError.
    """
    p = await page("e2e")
    await p.goto("/wrong_environment_error")
    await expect(p.locator("#errors")).to_have_text(
        "app,Response",
        timeout=10_000,
    )


async def test_use_effect(page: PageFixture):
    """blu.use_effect should work as described in the documentation."""
    p = await page("e2e")
    events_div = p.locator("#events")
    await p.goto("/use_effect")
    await expect(events_div).to_have_text("", timeout=10_000)
    await p.click("button")
    await expect(events_div).to_have_text("SETUP")
    await p.click("button")
    await expect(events_div).to_have_text("SETUP,TEARDOWN,SETUP")
    await p.click("button")
    await expect(events_div).to_have_text(
        "SETUP,TEARDOWN,SETUP,TEARDOWN,SETUP",
    )


async def test_use_ref(page: PageFixture):
    """
    blu.use_ref should store references and be editable as described in
    the documentation.
    """
    p = await page("e2e")
    await p.goto("/use_ref")
    counter = p.locator("#count")
    await expect(counter).to_have_text("0", timeout=10_000)
    await p.click("#increment")
    await p.click("#increment")
    await p.click("#increment")
    await asyncio.sleep(0.1)
    await expect(counter).to_have_text("0")
    await p.click("#rerender")
    await expect(counter).to_have_text("3")
    await p.click("#rerender")
    await asyncio.sleep(0.1)
    await expect(counter).to_have_text("3")


async def test_use_state(page: PageFixture):
    """
    blu.use_state should behave as described in the documentation.
    """
    p = await page("e2e")
    await p.goto("/use_state")
    counter = p.locator("#count")
    await expect(counter).to_have_text("0", timeout=10_000)
    await p.click("button")
    await expect(counter).to_have_text("1")
    await p.click("button")
    await expect(counter).to_have_text("2")


async def test_use_ref_html_element(page: PageFixture):
    """
    Passing a Ref as the "ref" prop of an HTML element should result in
    that Ref referencing the HTML element in an effect and during the
    following render.
    """
    p = await page("e2e")
    await p.goto("/html_editing_effect")
    await expect(p.locator("#test-div")).to_have_text("Hello.", timeout=10_000)


async def test_client_side_availability(page: PageFixture):
    """The js and pyscript packages are available client-side."""
    p = await page("e2e")
    await p.goto("/client_import")
    await expect(p.locator("#status")).to_have_text("Success!")


async def test_static_files(client: ClientFixture):
    """Static files are accessible as described in the documentation."""
    c = await client("e2e")
    response = await c.get("/static_file/_dynamic_path_/hello.txt")
    assert (await response.text()) == "Hello, World!"


async def test_client_file_specifier_ui(page: PageFixture):
    """
    Python files within the app package are available client-side if
    they contain the top-level statement "__client__ = True"; otherwise,
    they are not available client-side.
    """
    p = await page("e2e")
    await p.goto("/app_pkg_clientside/success")
    await expect(p.locator("#status")).to_have_text("Success!", timeout=10_000)
    await p.goto("/app_pkg_clientside/fail")
    await expect(p.locator("#status")).to_have_text("Fail.", timeout=10_000)


async def test_dev_server(patch_app: Callable[[str], None]):
    """
    Running `blu` on the command line causes a dev server to run. The
    output of the command line tells which port it is running on. The
    server runs the blu application described in the app package, and
    the server reloads any time there is a change to Python files in the
    app package.
    """
    # patch_app('e2e')
    e2e_app_dir = Path(__file__).parent / "apps/e2e"
    with TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        app_dir = temp_dir / "app"
        shutil.copytree(e2e_app_dir, app_dir)
        with subprocess.Popen(
            ["blu"],
            cwd=app_dir,
            stderr=subprocess.PIPE,
            text=True,
            env={
                "PATH": os.environ["PATH"],
                "PYTHONPATH": f"{str(temp_dir)}:{':'.join(sys.path)}",
            },
        ) as proc:
            assert proc.stderr is not None
            start = time.time()
            url: str | None = None
            for line in proc.stderr:
                if time.time() > start + 5:
                    raise TimeoutError("Took too long to get URL.")
                exp = r"Uvicorn running on (http://127\.0\.0\.1:\d+) "
                results = re.search(exp, line)
                if results is not None:
                    url = results.group(1)
                    break
            async with async_playwright() as playwright:
                chromium = playwright.chromium
                browser = await chromium.launch(headless=True)
                context = await browser.new_context(base_url=url)
                p = await context.new_page()
                try:
                    await p.goto("/dev_server")
                    main_div = p.locator("#main-div")
                    await expect(main_div).to_have_text("ORIGINAL")
                    index_file = app_dir / "dev_server/__index__.py"
                    new_source = index_file.read_text().replace(
                        "ORIGINAL",
                        "CHANGED",
                    )
                    index_file.write_text(new_source)
                    start = time.time()
                    while time.time() < start + 10:
                        await sleep(2)
                        try:
                            await p.reload()
                            await expect(main_div).to_have_text("CHANGED")
                        except AssertionError:
                            pass
                        else:
                            return
                    assert False
                finally:
                    await browser.close()


async def test_unusual_root_nodes(page: PageFixture):
    """Any blu.Node can be returned by a __page__ handler."""
    p = await page("e2e")
    await p.goto("/unusual_root_nodes/float")
    await expect(p.get_by_text("1.23485")).to_be_visible(timeout=10_000)
    await p.goto("/unusual_root_nodes/int")
    await expect(p.get_by_text("234857")).to_be_visible(timeout=10_000)
    await p.goto("/unusual_root_nodes/iterable")
    await expect(p.get_by_text("ABC")).to_be_visible(timeout=10_000)
    await p.goto("/unusual_root_nodes/key")
    await expect(p.get_by_text("Hello!")).to_be_visible(timeout=10_000)
    await p.goto("/unusual_root_nodes/none")
    await expect(p.get_by_text(re.compile(r".+"))).to_have_count(0, timeout=10_000)
    await p.goto("/unusual_root_nodes/str")
    await expect(p.get_by_text("Hello!")).to_be_visible(timeout=10_000)
    await p.goto("/unusual_root_nodes/tuple")
    await expect(p.get_by_text("ABC")).to_be_visible(timeout=10_000)


async def test_settings(page: PageFixture):
    """
    Settings in app/__settings__.py work as described in documenation.
    """
    p = await page("e2e_settings")
    await p.goto("/")
    arrr_exp = expect(p.get_by_text("Ahoy there."))
    await arrr_exp.to_be_visible(timeout=10_000)
    await expect(p.get_by_text("👍")).to_be_visible()


async def test_multilayer_tuple_children(page: PageFixture):
    """
    HTMLElement correctly renders when a tuple of tuples is passed in as
    children.
    """
    p = await page("e2e")
    await p.goto("/yield_in_tuple")
    await expect(p.get_by_text("This should be red.")).to_be_visible(timeout=10_000)


async def test_server_function(page: PageFixture):
    """Server functions work as described in documentation."""
    p = await page("e2e")
    await p.goto("/server_functions")
    await expect(p.get_by_text("Hello!")).to_be_visible()


async def test_async_effect(page: PageFixture):
    """use_effect accepts async callbacks."""
