from playwright.async_api import Page, expect

from tests.utils import prod_cli, prod_server


async def test_import_html_tags(page: Page):
    """You can import any HTML tag from blu.html"""

    async with prod_cli('tests.apps.import_html_tags') as url:
        await page.goto(url)
        start = 'html > body > '
        await page.locator(start + 'div').wait_for(
            state='attached',
            timeout=5000,
        )
        await expect(page.locator(start + 'span')).to_be_attached()
        await expect(page.locator(start + 'select')).to_be_attached()
        await expect(page.locator(start + 'canvas')).to_be_attached()
        await expect(page.locator(start + 'mymadeuptagname')).to_be_attached()


async def test_html_imports_getattr(page: Page):
    """
    If the HTML tag name you want to import is not a valid Python
    identifier or is a reserved word in Python, you can use the builtin
    getattr() function.
    """
    async with prod_cli('tests.apps.import_html_tags_getattr') as url:
        await page.goto(url)
        dashes_el = page.locator('tag-name-with-dashes')
        await dashes_el.wait_for(state='attached')
        del_el = dashes_el.locator('del')
        await expect(del_el).to_be_attached()
        await expect(del_el).to_have_text('Hello, World!')


async def test_html_imports_getattr__server(page: Page):
    """
    If the HTML tag name you want to import is not a valid Python
    identifier or is a reserved word in Python, you can use the builtin
    getattr() function. (server)
    """
    async with prod_server('tests.apps.import_html_tags_getattr') as url:
        await page.goto(url)
        dashes_el = page.locator('tag-name-with-dashes')
        await dashes_el.wait_for(state='attached')
        del_el = dashes_el.locator('del')
        await expect(del_el).to_be_attached()
        await expect(del_el).to_have_text('Hello, World!')


async def test_html_attrs(page: Page):
    """
    You can set the HTML attributes of an element by calling it as a
    function
    """
    async with prod_cli('tests.apps.html_attrs') as url:
        await page.goto(url)
        div = page.locator('div')
        await div.wait_for(state='attached')
        await expect(div).to_have_attribute('id', 'my-id')


async def test_html_attrs__server(page: Page):
    """
    You can set the HTML attributes of an element by calling it as a
    function (server)
    """
    async with prod_server('tests.apps.html_attrs') as url:
        await page.goto(url)
        div = page.locator('div')
        await div.wait_for(state='attached')
        await expect(div).to_have_attribute('id', 'my-id')