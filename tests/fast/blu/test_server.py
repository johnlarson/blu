import importlib
from unittest import mock

from blu import server
from blu import _server_functions
from tests.utils import reload_is_client


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


async def test_client_side():
    """
    On the client, transforms the function into a stub that defers the
    actual function call to the server.
    """

    with reload_is_client("Emscripten"):
        importlib.reload(_server_functions)
        with mock.patch(
            "blu._server_functions._invoke_server_function_remote",
        ) as mock_fn:

            @server
            async def sum(a, b):
                return a + b

            await sum(1, 2)
            mock_fn.assert_called_with(
                "test_server",
                "sum",
                (1, 2),
                {},
            )
