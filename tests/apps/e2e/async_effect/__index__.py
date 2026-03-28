from blu import client, use_effect
from blu.html import div


__client__ = True


def __page__():
    return MyClientElement


@client
def MyClientElement():
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
