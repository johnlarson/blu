from blu import client, use_effect, is_client, use_ref
from blu.html import div

from app.server_functions.hello_module import hello

if is_client:
    from js import alert

__client__ = True


def __page__():
    return ClientElement


@client
def ClientElement():
    div_ref = use_ref()

    @use_effect
    async def _():
        a = await hello({"message": "Hello!"})
        div_ref.innerText = a.value["message"]

    return div(ref=div_ref)
