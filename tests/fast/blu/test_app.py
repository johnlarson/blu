from pytest import MonkeyPatch
import pytest
from blu import WrongEnvironmentError, app
from blu import _utils

from tests.utils import Sender, receive


async def test_runs_blu_from_app_module(patch_app):  # type: ignore
    """
    app is an ASGI app that runs the Blu application defined in the
    current Python environment's "app" package.
    """
    patch_app("static_files")
    sender = Sender()
    await app(
        {
            "asgi": {
                "version": "1",
                "spec_version": "2.0",
            },
            "path": "/path/to/static/file.txt",
            "headers": [],
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "query_string": b"",
        },
        receive,
        sender,
    )
    assert sender.body() == "Hello, World!"


async def test_raises_WrongEnvironmentError_on_client(monkeypatch: MonkeyPatch):
    """
    Calling app client-side results in a blu.WrongEnvironmentError being
    raised.
    """
    monkeypatch.setattr(_utils, "is_client", True)
    with pytest.raises(WrongEnvironmentError):
        await app(
            {
                "asgi": {
                    "version": "1",
                    "spec_version": "2.0",
                },
                "path": "/",
                "headers": [],
                "type": "http",
                "http_version": "1.1",
                "method": "GET",
                "query_string": b"",
            },
            receive,
            Sender(),
        )
