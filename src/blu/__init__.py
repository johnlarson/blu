"""A full stack React framework for Python."""

from blu._utils.client import is_client
from blu._utils.typing import Protocol, Any
from blu import html
from blu._exceptions import WrongEnvironmentError
from blu._core import create_html_element as create_rare_html_element
from blu._core.nodes import (
    ClientRenderer, HTMLElement, Key, ClientElement, Node
)
from blu._core.client_decorator import client
from blu._core.hooks import Ref, use_effect, use_ref, use_state


class ServerOnlyClientInterface:
    name: str
    
    def __init__(self, name: str):
        self.name = name

    def __call__(self, *args: Any, **kwargs: Any):
        raise WrongEnvironmentError(f'Cannot instantiate {self.name} in client environment.')
    
    def __getattribute__(self, name: str) -> Any:
        raise WrongEnvironmentError(f'Cannot use {self.name} in client environment.')


if is_client:
    Response = ServerOnlyClientInterface('Response')
    app = ServerOnlyClientInterface('app')
else:
    from blu._core.http import Response
    from blu._app import app


__all__ = [
    'ClientElement',
    'ClientRenderer',
    'HTMLElement',
    'Key',
    'Node',
    'Ref',
    'Response',
    'WrongEnvironmentError',
    'app',
    'client',
    'create_rare_html_element',
    'html',
    'is_client',
    'use_effect',
    'use_state',
    'use_ref',
]


class Settings(Protocol):
    """
    Interface for the app.__settings__ module (app/__settings__.py).
    """
    
    CLIENT_REQUIREMENTS: list[str]
