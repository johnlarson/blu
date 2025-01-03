from typing import Any, Protocol
from blu import html
from blu._react.types import HTMLElement


__all__ = [
    'ClientDecorator',
    'ClientElement',
    'HTMLElement',
    'Node',
    'Response',
    'Settings',
    'app',
    'client',
    'html',
    'use_effect',
    'use_state',
    'use_ref',
]

class ClientDecorator:
    ...


class ClientElement:
    ...


type Node = Any


class Response:
    ...


class Settings(Protocol):
    ...


app = ...


client = ...


def use_effect():
    ...


def use_state():
    ...


def use_ref():
    ...