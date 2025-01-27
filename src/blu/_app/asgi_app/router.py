from collections.abc import Callable
from typing import Any, Protocol
from blu._http import Request, Response


class AnyCallable(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


class RouteNotFound(Exception):
    pass


class Router:
    _index_page: AnyCallable
    _default_page: AnyCallable
    _static_segments: dict[str, 'Router']
    _dynamic_segments: list['Router']

    def __init__(self, app_module: str):
        ...

    def handle(self, request: Request) -> Response:
        ...