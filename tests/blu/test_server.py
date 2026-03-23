from blu import server


async def test_sync_to_async():
    """
    If given a synchronous function, returns an asynchronous version of
    the same function, i.e. given the same inputs, it will return the
    same value and have the same side effects that the original had; the
    only difference is that the new function must be awaited.
    """

    @server
    def sum(a, b):
        return a + b

    assert await sum(1, 2) == 3


async def test_async_to_async():
    """
    If given an asynchronous function, returns the function given,
    unchanged.
    """

    @server
    async def sum(a, b):
        return a + b

    assert await sum(1, 2) == 3


def test_client_side():
    """
    On the client, transforms the function into a stub that defers the
    actual function call to the server.

    TODO: implement this.
    """
