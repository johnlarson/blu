from collections.abc import AsyncGenerator, Generator, Iterable, Mapping
from contextlib import contextmanager
import os
from pathlib import Path
import re
from subprocess import PIPE, Popen
import sys
from tempfile import TemporaryDirectory
from textwrap import dedent
from threading import Thread
from typing import Optional, cast

from playwright.async_api import async_playwright, Page, expect
import pytest
import requests

from tests.utils import test_projects


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


type FileTree = Mapping[str, str | FileTree]


@contextmanager
def run_dev(files: FileTree) -> Generator[str, None, None]:
    with TemporaryDirectory() as temp_path:
        write_to_directory(files, Path(temp_path))
        with run_in_background(
            ['blu', 'dev'],
            cwd=temp_path,
            env={**os.environ, 'PYTHONPATH': ':'.join(sys.path)},
        ) as proc:
            port = get_app_port(proc)
            yield f'http://127.0.0.1:{port}'


def write_to_directory(files: FileTree, path: Path):
    for k, v in files.items():
        new_path = path / k
        if isinstance(v, str):
            with new_path.open('w')as f:
                f.write(dedent(v.strip()))
        else:
            write_to_directory(v, new_path)


@contextmanager
def run_in_background(
    command: list[str],
    /,
    cwd: Optional[str | Path] = None,
    env: Optional[dict[str, str]] = None,
) -> Generator[Popen[str], None, None]:
    with Popen(
        command, cwd=cwd, stdout=PIPE, stderr=PIPE, env=env, text=True
    ) as proc:
        try:
            yield proc
        finally:
            proc.kill()


def get_app_port(proc: Popen[str]) -> int:
    ret_container: list[None | int] = [None]
    thread = Thread(
        target=_get_app_port_target,
        args=[proc, ret_container],
    )
    thread.start()
    thread.join()
    ret = ret_container[0]
    if isinstance(ret, int):
        return ret
    raise Exception('Unable to set port number.')


def _get_app_port_target(
    proc: Popen[str], ret_container: list[int | None]
) -> None:
    for line in cast(Iterable[str], proc.stderr):
        re_match = re.search(r'http://127\.0\.0\.1:(\d+)', line)
        if re_match is not None:
            ret_container[0] = int(re_match[1])
            return
    raise Exception('Process completed without specifying port in stderr.')


async def test_html_element(page: Page):
    """Serves a page with an HTML element."""
    with run_dev({
        'app': {
            '__index__.py': '''
                from blu.html import mytagname


                def __page__():
                    return mytagname
            ''',
        },
    }) as url:
        await page.goto(url)
        element = page.locator('mytagname')
        await expect(element).to_be_attached()


async def test_html_element_with_attrs(page: Page):
    """Serves a page with an HTML element with attributes."""
    with run_dev({
        'app': {
            '__index__.py': '''
                from blu.html import mytagname


                def __page__():
                    return mytagname(className='hello')
            ''',
        },
    }) as url:
        await page.goto(url)
        element = page.locator('mytagname')
        await expect(element).to_have_attribute('class', 'hello')


async def test_html_element_with_a_child(page: Page):
    """Serves a page with a single HTML element with a child node."""
    with run_dev({
        'app': {
            '__index__.py': '''
                from blu.html import mytagname


                def __page__():
                    return mytagname['Hello World!']
            ''',
        },
    }) as url:
        await page.goto(url)
        element = page.locator('mytagname')
        await expect(element).to_have_text('Hello World!')


async def test_html_element_with_multiple_children(page: Page):
    """Serves a page with an HTML element with multiple children."""
    with run_dev({
        'app': {
            '__index__.py': '''
                from blu.html import 


                def __page__():
                    return mytagname['Hello', 'World!']
            ''',
        },
    }) as url:
        await page.goto(url)
        element = page.locator('mytagname')
        await expect(element).to_have_text('HelloWorld!')


async def test_html_element_with_html_element_child(page: Page):
    """
    Serves a page with an HTML element with another HTML element as a
    child.
    """
    with run_dev({
        'app': {
            '__index__.py': '''
                from blu.html import first, second


                def __page__():
                    return first[
                        second['Hello World!'],
                    ]
            ''',
        },
    }) as url:
        await page.goto(url)
        element = page.locator('mytagname')
        await expect(element).to_have_text('Hello World!')


async def test_html_element_children_multiple_layers(page: Page):
    """Serves a page multiple layers of child nodes."""
    with run_dev({
        'app': {
            '__index__.py': '''
                from blu.html import first, second, third


                def __page__():
                    return first[
                        second[
                            third'Hello World!'],
                        ],
                    ]
            ''',
        },
    }) as url:
        await page.goto(url)
        element = page.locator('mytagname')
        await expect(element).to_have_text('Hello World!')