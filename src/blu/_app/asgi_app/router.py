from collections.abc import Callable
from importlib import import_module
import pkgutil
from typing import Any, Optional, Protocol, cast
from blu._http import Request, Response


class AnyCallable(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


class RouteNotFound(Exception):
    pass


class Router:
    index_page: Optional[AnyCallable]
    default_page: Optional[AnyCallable]
    static_segments: dict[str, 'Router']
    dynamic_segments: list['Router']

    def __init__(self, module_name: str):
        self.index_page = None
        self.default_page = None
        self.static_segments = {}
        self.dynamic_segments = []
        module = import_module(module_name)
        if hasattr(module, '__path__'):
            for module_info in pkgutil.iter_modules(module.__path__):
                name = module_info.name
                full_name = module_name + '.' + name
                if name == '__index__':
                    self.index_page = self._get_page_handler(full_name)
                elif name == '__default__':
                    self.default_page = self._get_page_handler(full_name)
                elif is_static_segment(name):
                    self.static_segments[name] = Router(full_name)
                elif is_dynamic_segment(name):
                    self.dynamic_segments.append(Router(full_name))

    def _get_page_handler(self, module_name: str) -> AnyCallable:
        module = import_module(module_name)
        return cast(AnyCallable, module.__page__)

    def handle(self, request: Request) -> Response:
        ...


def is_static_segment(name: str) -> bool:
    return len(name) > 0 and name[0] != '_' and name[-1] != '_'


def is_dynamic_segment(name: str) -> bool:
    return (
        len(name) > 2 and
        name[0] == '_' and
        name[1] != '_' and
        name[-1] == '_' and
        name[-2] != '_'
    )