from collections.abc import Callable
from typing import Any
from blu import html
from blu._react.types import HTMLElement


__all__ = [
    'ClientElement', 'HTMLElement', 'Node', 'Response', 'app', 'client',
    'html', 'use_state', 'use_ref', 'use_effect',
]


class ClientElement:
    ...


type Node = Any


class Response:
    ...


app = ...





def client(fn: ) -> ClientElement:
    ...

