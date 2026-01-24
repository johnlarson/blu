from contextlib import contextmanager
import importlib
import platform
from unittest import mock

import blu
from blu import _utils
from blu._utils import client as client_utils


@contextmanager
def reload_is_client(system):
    with mock.patch('platform.system', return_value=system):
        _reload_is_client()
        yield
    _reload_is_client()


def _reload_is_client():
        importlib.reload(client_utils)
        importlib.reload(_utils)
        importlib.reload(blu)


def test_is_false_in_server_environment():
    """blu.is_client evaluates to False in a server environment."""
    assert not blu.is_client


def test_is_true_in_client_environment():
    """blu.is_client evaluates to True in a client environment."""
    with reload_is_client('Emscripten'):
        assert blu.is_client