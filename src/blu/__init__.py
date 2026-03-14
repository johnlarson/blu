"""A full stack React framework for Python."""

from typing import Callable

from blu._utils.client import is_client
from blu._utils.typing import Protocol, Any
from blu import html
from blu._exceptions import WrongEnvironmentError
from blu._nodes import (
    ClientRenderer,
    HTMLElement,
    Key,
    ClientElement,
    Node,
    client,
    create_html_element as create_rare_html_element,
)
from blu._hooks import Ref, use_effect, use_ref, use_state


class ServerOnlyClientInterface:
    _name: str

    def __init__(self, name: str):
        self._name = name

    def __call__(self, *args: Any, **kwargs: Any):
        raise WrongEnvironmentError(
            f"Cannot instantiate {self._name} in client environment."
        )

    def __getattr__(self, name: str) -> Any:
        raise WrongEnvironmentError(f"Cannot use {self._name} in client environment.")


if is_client:
    Response = ServerOnlyClientInterface("Response")
    app = ServerOnlyClientInterface("app")
else:
    from blu._http import Response
    from blu._app import app


__all__ = [
    "ClientElement",
    "ClientRenderer",
    "HTMLElement",
    "Key",
    "Node",
    "Ref",
    "Response",
    "WrongEnvironmentError",
    "app",
    "client",
    "create_rare_html_element",
    "html",
    "is_client",
    "use_effect",
    "use_state",
    "use_ref",
]


noop: Callable[[Any], None] = lambda x: x


class Settings(Protocol):
    """
    Interface for the app.__settings__ module (app/__settings__.py).
    """

    CLIENT_REQUIREMENTS: list[str]
