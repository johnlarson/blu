from playwright.async_api import Page, expect

from tests.utils import prod_cli


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