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


async def test_dynamic_route_segment(page: Page):
    """
    From docs:

    To add a dynamic route segment, create a directory whose name is
    surrounded by single underscores, like the _employee_id_ directory
    in this example
    """
    async with prod_cli('tests.apps.dynamic_route_segment') as url:
        await page.goto(url + f'/employees/cheese')
        await expect(page.locator('p')).to_have_text(
            'This is an employee profile page.'
        )


async def test_dynamic_route_segment__server(page: Page):
    """
    From docs:

    To add a dynamic route segment, create a directory whose name is
    surrounded by single underscores, like the _employee_id_ directory
    in this example

    (server)
    """
    async with prod_server('tests.apps.dynamic_route_segment') as url:
        await page.goto(url + f'/employees/cheese')
        await expect(page.locator('p')).to_have_text(
            'This is an employee profile page.'
        )