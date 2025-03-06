import re
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


async def test_html_attrs_no_mutate_original(page: Page):
    """
    Calling an HTML element as a function does not mutate the original;
    instead, it returns a copy with the new attributes.
    """
    async with prod_cli('tests.apps.html_attrs_no_mutate') as url:
        await page.goto(url)
        without_attrs = page.locator('div#without-attributes')
        await expect(without_attrs).to_be_attached()
        any_attr = re.compile(r'.|')
        await expect(without_attrs).not_to_have_attribute('a', any_attr)
        await expect(without_attrs).not_to_have_attribute('b', any_attr)
        with_attrs = page.locator('div#with-attributes')
        await expect(with_attrs).to_have_attribute('a', '1')
        await expect(with_attrs).to_have_attribute('b', '2')


async def test_html_attrs_no_mutate_original__server(page: Page):
    """
    Calling an HTML element as a function does not mutate the original;
    instead, it returns a copy with the new attributes. (server)
    """
    async with prod_server('tests.apps.html_attrs_no_mutate') as url:
        await page.goto(url)
        without_attrs = page.locator('div#without-attributes')
        await expect(without_attrs).to_be_attached()
        any_attr = re.compile(r'.|')
        await expect(without_attrs).not_to_have_attribute('a', any_attr)
        await expect(without_attrs).not_to_have_attribute('b', any_attr)
        with_attrs = page.locator('div#with-attributes')
        await expect(with_attrs).to_have_attribute('a', '1')
        await expect(with_attrs).to_have_attribute('b', '2')


async def test_html_attrs_full_replace(page: Page):
    """
    When you set HTML attributes on an element, you completely replace
    the existing attributes, rather than adding attributes on top
    """
    async with prod_cli('tests.apps.html_attrs_full_replace') as url:
        await page.goto(url)
        updated_div = page.locator('div')
        any_attr = re.compile(r'.|')
        await expect(updated_div).not_to_have_attribute('a', any_attr)
        await expect(updated_div).not_to_have_attribute('b', any_attr)
        await expect(updated_div).to_have_attribute('c', '3')
        await expect(updated_div).to_have_attribute('d', '4')


async def test_html_element_react_attrs(page: Page):
    """
    Blu HTML elements take the same attributes as React HTML elements,
    not native HTML elements (see
    https://react.dev/reference/react-dom/components for more
    information)
    """
    async with prod_cli('tests.apps.html_react_attrs') as url:
        await page.goto(url)
        await expect(page.locator('div')).to_have_class('my-class')