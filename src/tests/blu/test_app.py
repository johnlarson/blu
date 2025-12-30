from pytest import MonkeyPatch
import pytest
import blu
from blu import WrongEnvironmentError, app
from tests.utils import Sender, projects, receive


async def test_runs_blu_from_app_module(monkeypatch: MonkeyPatch):
    """
    app is an ASGI app that runs the Blu application defined in the
    current Python environment's "app" package.
    """
    monkeypatch.syspath_prepend(projects / 'basic')  # type: ignore
    sender_success = Sender()
    await app(
        {
            'asgi': {
                'version': '1',
                'spec_version': '2.0',
            },
            'path': '/',
            'headers': [],
            'type': 'http',
            'http_version': '1.1',
            'method': 'GET',
            'query_string': b'',
        },
        receive,
        sender_success,
    )
    assert next(sender_success).get('status', None) == 200
    
    sender_404 = Sender()
    await app(
        {
            'asgi': {
                'version': '1',
                'spec_version': '2.0',
            },
            'path': '/',
            'headers': [],
            'type': 'http',
            'http_version': '1.1',
            'method': 'GET',
            'query_string': b'',
        },
        receive,
        sender_404,
    )
    assert next(sender_404).get('status', None) == 404


async def test_raises_WrongEnvironmentError_on_client(monkeypatch: MonkeyPatch):
    """
    Calling app client-side results in a blu.WrongEnvironmentError being
    raised.
    """
    monkeypatch.setattr(blu, 'is_client', True)
    with pytest.raises(WrongEnvironmentError):
        await app(
            {
                'asgi': {
                    'version': '1',
                    'spec_version': '2.0',
                },
                'path': '/',
                'headers': [],
                'type': 'http',
                'http_version': '1.1',
                'method': 'GET',
                'query_string': b'',
            },
            receive,
            Sender(),
        )
