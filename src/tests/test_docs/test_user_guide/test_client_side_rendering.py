from typing import cast
from aiohttp import ClientSession as Client
from playwright.async_api import Page, expect

from tests.utils import prod_cli, prod_server


async def test_event_handler_on_server(client: Client):
    """
    From docs:

    You may have noticed that when you try to set an event handler on an
    html element
    """
    async with prod_cli('tests.apps.event_handler_on_server') as url:
        res = await client.get(url)
        assert res.status == 500


async def test_client_element(page: Page):
    """
    From docs:

    A client element is an custom element that is rendered on the
    client.
    """
    dialog_message: str | None = None

    def handle_dialog(dialog):  # type: ignore
        nonlocal dialog_message
        dialog_message = cast(str, dialog.message)  # type: ignore
        dialog.dismiss()  # type: ignore
    
    async with prod_cli('tests.apps.event_handler_on_server') as url:
        await page.goto(url)
        page.once('dialog', handle_dialog)  # type: ignore
        await page.click('button')
        assert dialog_message == 'Hello!'
        