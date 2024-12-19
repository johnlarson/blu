from collections.abc import AsyncGenerator, Generator, Iterable
from contextlib import contextmanager
import os
from pathlib import Path
import re
from subprocess import PIPE, Popen
import sys
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


async def test_dev_match_cli_no_port_provided(page: Page):
    with run_in_background(
        ['blu', 'dev'],
        cwd=test_projects / 'basic',
        env={
            **os.environ,
            'PYTHONPATH': ':'.join(sys.path),
        },
    ) as proc:
        port = get_app_port(proc)
        await page.goto(f'http://127.0.0.1:{port}')
        div = page.locator('div')
        await expect(div).to_have_text('Hello World!')
