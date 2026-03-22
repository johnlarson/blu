from blu import client, use_effect, is_client

from app.hello_module import hello

if is_client:
    from js import alert

__client__ = True


def __page__():
    return ClientElement


@client
def ClientElement():

    @use_effect
    async def _():
        a = hello({"message": "Hello!"})
        alert(await a.value["message"])
