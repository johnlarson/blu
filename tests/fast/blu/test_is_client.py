from contextlib import contextmanager
import importlib
import platform
from unittest import mock
import blu
from tests.utils import reload_is_client


def test_is_false_in_server_environment():
    """blu.is_client evaluates to False in a server environment."""
    assert not blu.is_client


def test_is_true_in_client_environment():
    """blu.is_client evaluates to True in a client environment."""
    with reload_is_client("Emscripten"):
        assert blu.is_client
