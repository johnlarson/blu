import asyncio

from blu import client, use_effect, use_ref
from blu.html import div

from app.server_functions.hello_module import hello

__client__ = True


def __page__():
    return ClientElement


@client
def ClientElement():
    div_ref = use_ref()

    @use_effect
    def _():
        async def run():
            a = await hello({"message": "Hello!"})
            div_ref[:].innerText = a.value["message"]

        asyncio.create_task(run())

    return div(ref=div_ref)
