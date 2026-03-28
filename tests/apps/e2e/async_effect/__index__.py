import asyncio

from blu import client, use_effect, use_ref
from blu._nodes import ClientElement
from blu.html import div

from app.server_functions.hello_module import hello

__client__ = True


def __page__():
    return ClientElement


@client
def ClientElement():
    from js import alert

    @use_effect
    async def _():
        alert("SETUP ONLY")

    @use_effect
    async def _():
        alert("SETUP")
        yield
        alert("TEARDOWN")

    return div["Hello!"]
