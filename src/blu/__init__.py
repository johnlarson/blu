"""A full stack React framework for Python."""

from blu._utils.client import is_client
from blu._utils.typing import Protocol, Any
from blu import html
from blu._exceptions import WrongEnvironmentError
from blu._react.types import HTMLElement, Key, ClientElement, Element, Node
from blu._react.client_decorator import ClientDecorator, client
from blu._react.hooks import Effect, Ref, use_effect, use_ref, use_state


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
    from blu._http import Response
    from blu._default_app import app


__all__ = [
    'ClientDecorator',
    'ClientElement',
    'Effect',
    'Element',
    'HTMLElement',
    'Key',
    'Node',
    'Ref',
    'Response',
    'Settings',
    'WrongEnvironmentError',
    'app',
    'client',
    'html',
    'use_effect',
    'use_state',
    'use_ref',
]


class Settings(Protocol):
    """
    Interface for the app.__settings__ module (app/__settings__.py).
    """
    ...
