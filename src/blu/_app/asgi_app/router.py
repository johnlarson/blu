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

    async def handle(
        self,
        request: Request,
        path: list[str],
    ) -> Optional[Response]:
        return (
            await self._handle_index_page(request, path) or
            await self._handle_default_page(request, path)
        )
        
    async def _handle_index_page(
        self,
        request: Request,
        path: list[str],
    ) -> Optional[Response]:
        if not self.index_page:
            return None
        if path:
            return None
        ...

    async def _handle_static(
        self,
        request: Request,
        path: list[str],
    ) -> Optional[Response]:
        if not path:
            return None
        for name, segment in self.static_segments.items():
            if name == path[0]:
                response = await segment.handle(request, path[1:])
                if response is not None:
                    return response
        return None

    async def _handle_dynamic(
        self,
        request: Request,
        path: list[str],
    ) -> Optional[Response]:
        if not path:
            return None
        for segment in self.dynamic_segments:
            response = await segment.handle(request, path[1:])
            if response is not None:
                return response
        return None


    async def _handle_default_page(
        self,
        request: Request,
        path: list[str],
    ) -> Optional[Response]:
        if not self.default_page:
            return None
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