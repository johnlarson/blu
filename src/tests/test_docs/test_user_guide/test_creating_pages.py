import re
from playwright.async_api import Page, expect
import pytest

from blu import WrongEnvironmentError
from blu.html import div
from tests.utils import prod_cli, prod_server


async def test_import_html_tags(page: Page):
    """
    From docs:

    You can import any HTML tag from blu.html
    """

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
    From docs:

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
    From docs:

    If the HTML tag name you want to import is not a valid Python
    identifier or is a reserved word in Python, you can use the builtin
    getattr() function.
    
    (server)
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
    From docs:

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
    From docs:

    You can set the HTML attributes of an element by calling it as a
    function
    
    (server)
    """
    async with prod_server('tests.apps.html_attrs') as url:
        await page.goto(url)
        div = page.locator('div')
        await div.wait_for(state='attached')
        await expect(div).to_have_attribute('id', 'my-id')


async def test_html_attrs_no_mutate_original(page: Page):
    """
    From docs:

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
    From docs:

    Calling an HTML element as a function does not mutate the original;
    instead, it returns a copy with the new attributes.
    
    (server)
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
    From docs:

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
    From docs:

    Blu HTML elements take the same attributes as React HTML elements,
    not native HTML elements (see
    https://react.dev/reference/react-dom/components for more
    information)
    """
    async with prod_cli('tests.apps.html_react_attrs') as url:
        await page.goto(url)
        await expect(page.locator('div')).to_have_class('my-class')


async def test_server_side_event_handler_raises_exception():
    """
    From docs:

    Event-handling attributes like “onClick” are only supported in
    client-side rendering
    """

    def log_clicked(e):  # type: ignore
        print('Clicked!')
    
    with pytest.raises(WrongEnvironmentError):
        div(onClick=log_clicked)  # type: ignore


async def test_html_attrs_positional_arg(page: Page):
    """
    From docs:

    For attribute names that are not valid Python identifiers or are
    reserved words in python, pass in a Mapping as the first positional
    argument
    """
    async with prod_cli('tests.apps.html_attrs_pos_arg') as url:
        await page.goto(url)
        label = page.locator('label')
        await expect(label).to_have_attribute('for', 'value-input')
        input = page.locator('input')
        await expect(input).to_have_attribute('data-value', '23')
        await expect(input).to_have_attribute('id', 'value-input')


async def test_html_children(page: Page):
    """
    From docs:

    You can add children to an html element using square bracket
    notation
    """
    async with prod_cli('tests.apps.html_children') as url:
        await page.goto(url)
        await expect(page.locator('div p:nth-child(1)')).to_have_text('Hi.')
        await expect(page.locator('div p:nth-child(2)')).to_have_text('Hello.')


async def test_html_children_no_mutate(page: Page):
    """
    From docs:

    Using square bracket notation on an HTML element does not mutate th
    original; instead, it returns a copy with the new attributes.
    """
    async with prod_cli('tests.apps.html_children_no_mutate') as url:
        await page.goto(url)
        await expect(page.locator('span div:nth-child(1)')).to_have_text('')
        await expect(page.locator('span div:nth-child(2)')).to_have_text(
            'Hello, World!',
        )


async def test_html_children_replace(page: Page):
    """
    From docs:

    When you set children on an HTML element, you completely replace any
    existing children, rather than appending to them
    """
    async with prod_cli('tests.apps.html_children_replace') as url:
        await page.goto(url)
        await expect(page.locator('div.my-div')).to_have_text('CD')


async def test_html_child_node_types(page: Page):
    """
    From docs:

    A child of an HTML element can be any of the following types:

    - Another blu.HTMLElement.
    - A str. In this case, it will be rendered as an HTML text node.
    - None. Nothing is rendered in the place where a None value is
      found.
    - A int. This renders as a text node whose text is the str
      representation of the integer.
    - A float. This renders as a text node whose text is the str
      representation of the float.
    - An Iterable of valid children. This renders as all the child nodes
      contained in the Iterable.
    """
    async with prod_cli('tests.apps.html_child_node_types') as url:
        await page.goto(url)
        await expect(
            page.locator('div.my-div > span:nth-child(1)'),
        ).to_be_attached()
        await expect(page.locator('div.my-div')).to_have_text(
            'Hello!11Hello again!22',
        )
        await expect(
            page.locator('div.my-div > p:nth-child(2)'),
        ).to_be_attached()


async def test_html_keys(page: Page):
    """
    From docs:

    Items in Iterable children (other than strs and tuples) must be
    keyed
    """
    async with prod_cli('tests.apps.html_keys') as url:
        await page.goto(url)
        await expect(page.locator('.keyed')).to_have_text(
            'Hello, Ana!Hello, Bill!Hello, Charlotte!',
        )
        await expect(page.locator('.tuple')).to_have_text(
            'Hello, Ana!Hello, Bill!Hello, Charlotte!',
        )
        await expect(page.locator('.str')).to_have_text(
            'Hello, Ana! Hello, Bill! Hello, Charlotte!',
        )


async def test_html_keys_server(page: Page):
    """
    From docs:

    Items in Iterable children (other than strs and tuples) must be
    keyed

    (server)
    """
    async with prod_server('tests.apps.html_keys') as url:
        await page.goto(url)
        await expect(page.locator('.keyed')).to_have_text(
            'Hello, Ana!Hello, Bill!Hello, Charlotte!',
        )
        await expect(page.locator('.tuple')).to_have_text(
            'Hello, Ana!Hello, Bill!Hello, Charlotte!',
        )
        await expect(page.locator('.str')).to_have_text(
            'Hello, Ana! Hello, Bill! Hello, Charlotte!',
        )