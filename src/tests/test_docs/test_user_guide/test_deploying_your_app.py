import re
import aiofiles
from aiohttp import ClientSession as Client
from playwright.async_api import Page, expect
from blu._utils import get_available_port
from tests.utils import background, copy_app_dir, run, temp_dir


async def test_deploy_app(page: Page, client: Client):
    """App can be deployed following instructions in User Guide"""

    async with copy_app_dir('tests.apps.deployment') as project_root:

        # build

        await run(['blu', 'build'], project_root)
        assert (project_root / 'app').is_dir()  # make sure it's still there.
        async with aiofiles.open(
            project_root / 'static/my_dir/file.txt',
            'r',
        ) as static_f:
            assert await static_f.read() == 'HELLO THERE'
        assert (project_root / '.build').is_dir()

        # start up the ASGI server

        port = get_available_port()
        with background(
            ['uvicorn', 'blu:app', '--port', str(port)],
            project_root,
        ) as proc:
            stderr = proc.stderr
            assert stderr is not None
            for line in stderr:
                if re.search(r'http://127\.0\.0\.1:(\d+)', line):
                    break
            url = f'http://127.0.0.1:{port}'
            await page.goto(url)
            await expect(page.locator('p')).to_have_text('Hello, World!')
            res = await client.get(url + '/my_dir/file.txt')
            assert await res.text() == 'HELLO THERE'
