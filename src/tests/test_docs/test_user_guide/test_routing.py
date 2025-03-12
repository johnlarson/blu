from playwright.async_api import Page, expect

from tests.utils import prod_cli, prod_server


async def test_file_based_routing(page: Page):
    """
    From docs:

    Blu uses file-based routing. This means that the path that a page is
    served from is based on the file’s location in the app/.

    For example, if you want to serve the page in the Quickstart guide
    from /path/to/page instead of from /, you would move the
    __index__.py file from app/ to app/path/to/page
    """
    async with prod_cli('tests.apps.file_based_routing') as url:
        await page.goto(url + '/path/to/page')
        await expect(page.locator('body')).to_have_text('Hello World!')


async def test_file_based_routing__server(page: Page):
    """
    From docs:

    Blu uses file-based routing. This means that the path that a page is
    served from is based on the file’s location in the app/.

    For example, if you want to serve the page in the Quickstart guide
    from /path/to/page instead of from /, you would move the
    __index__.py file from app/ to app/path/to/page

    (server)
    """
    async with prod_server('tests.apps.file_based_routing') as url:
        await page.goto(url + '/path/to/page')
        await expect(page.locator('body')).to_have_text('Hello World!')