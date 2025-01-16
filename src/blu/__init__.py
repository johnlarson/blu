"""A full stack React framework for Python."""

from collections.abc import AsyncGenerator, Callable, Generator
from typing import Any, Protocol, Self
from blu import html
from blu._react.types import HTMLElement


__all__ = [
    'ClientDecorator',
    'ClientElement',
    'Effect',
    'Element',
    'HTMLElement',
    'Node',
    'Ref',
    'Response',
    'Settings',
    'app',
    'client',
    'html',
    'use_effect',
    'use_state',
    'use_ref',
]


type ElementRenderer[**P = ...] = Callable[
    P,
    Node | Generator[None, Node, Node] | AsyncGenerator[None | Node, Node]
]


class ClientDecorator:
    """
    The type of :func:`blu.client`. Can be used as a decorator to denote
    that an element's rendering should be deferred to the client or as a
    test for whether the code is currently running in a client
    environment.

    .. code-block:: python

        from blu import client
        from blu.html import p

        if client:
            import pyscript

        
        @client
        def MyClientElement():
            return p['Hello World!']
    """
    
    def __call__(
        self,
        render_function: ElementRenderer[...],
    ) -> 'ClientElement':
        ...
    
    def __bool__(self) -> bool:
        ...


class Element[**P](Protocol):

    args: P.args
    kwargs: P.kwargs
    children: list['Node']
    
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> 'Element[P]':
        ...
    
    def __getitem__(self, *children: 'Node') -> 'Element[P]':
        ...


class ClientElement[**P](Element[P]):
    """
    A custom element to be rendered client-side. Created using the
    :func:`blu.client` decorator.

    .. code-block:: python

        from blu import client
        from blu.html import b, span

        
        @client
        def ColorfulText(color, bold):
            colorful_span = span(style={'color': color})[
                (yield)
            ]
            if bold:
                return b[colorful_span]
            else:
                return colorful_span

                
        ColoredText('red', bold=True)[
            'Danger! The world said hello back.',
        ]

    .. code-block:: html

        <b>
            <span style="color: red">
                Danger! The world said hello back.
            </span>
        </b>
    """
    
    args: P.args
    kwargs: P.kwargs
    children: list['Node']

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> 'ClientElement[P]':
        ...

    def __getitem__(self, *children: 'Node') -> 'ClientElement[P]':
        ...


type Node = Any
""""""


class Response:
    """
    An HTTP Response.
    """
    ...


class Settings(Protocol):
    """
    Interface for the app.__settings__ module (app/__settings__.py).
    """
    ...


app = ...
"""The ASGI app used to deploy your Blu app."""


client = ...
"""
Creates client-rendered custom components.

Can also be used to test whether currently running in a client
environment.
"""

type Effect = Callable[[], Generator[None] | AsyncGenerator[None]]


def use_effect(callback: Effect):
    ...


def use_state[T](init: T) -> tuple[T, Callable[[T], None]]:
    ...


class Ref[T]:
    _current: T
    
    def __getitem__(self, empty_slice: slice) -> T:
        if empty_slice.start or empty_slice.stop or empty_slice.step:
            raise
        return self._current


def use_ref[T](init: T) -> Ref[T]:
    ...
