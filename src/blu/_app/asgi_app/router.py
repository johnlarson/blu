from collections.abc import Callable
from importlib import import_module
from pathlib import Path
import pkgutil
from typing import Any, Optional, Protocol, cast
from blu._http import Request, Response
from blu._react.types import Node
from blu._utils.asyncio import awaitable


class Handler(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Response | Node: ...


class RouteNotFound(Exception):
    pass


class Router:
    index_page: Optional[Handler]
    default_page: Optional[Handler]
    static_segments: dict[str, 'Router']
    dynamic_segments: list['Router']

    def __init__(self, dir: Path, package_name: str):
        self.index_page = None
        self.default_page = None
        self.static_segments = {}
        self.dynamic_segments = []
        for path in dir.iterdir():
            name = path.stem
            full_name = package_name + '.' + name
            if name == '__index__':
                self.index_page = self._get_page_handler(full_name)
            elif name == '__default__':
                self.default_page = self._get_page_handler(full_name)
            elif is_static_segment(name):
                self.static_segments[name] = Router(path, full_name)
            elif is_dynamic_segment(name):
                self.dynamic_segments.append(Router(path, full_name))

    def _get_page_handler(self, module_name: str) -> Handler:
        module = import_module(module_name)
        return module.__page__

    async def handle(
        self,
        request: Request,
        path: list[str],
    ) -> Optional[Response]:
        response_ret = await self._get_handler_ret(request, path)
        if isinstance(response_ret, Response):
            return response_ret
        else:
            return Response(response_ret)
        
    async def _get_handler_ret(
        self,
        request: Request,
        path: list[str],
    ) -> Response | Node:
        try:
            return await self._handle_index_page(request, path)
        except NotFound:
            pass
        try:
            return await self._handle_static(request, path)
        except NotFound:
            pass
        try:
            return await self._handle_dynamic(request, path)
        except NotFound:
            pass
        return await self._handle_default_page(request, path)
        
    async def _handle_index_page(
        self,
        request: Request,
        path: list[str],
    ) -> Response | Node:
        if not self.index_page:
            raise NotFound
        if path:
            raise NotFound
        return await awaitable(self.index_page())

    async def _handle_static(
        self,
        request: Request,
        path: list[str],
    ) -> Response | Node:
        if not path:
            raise NotFound
        for name, segment in self.static_segments.items():
            if name == path[0]:
                response = await segment.handle(request, path[1:])
                if response is not None:
                    return response
        raise NotFound

    async def _handle_dynamic(
        self,
        request: Request,
        path: list[str],
    ) -> Optional[Response | Node]:
        if not path:
            raise NotFound
        for segment in self.dynamic_segments:
            response = await segment.handle(request, path[1:])
            if response is not None:
                return response
        raise NotFound


    async def _handle_default_page(
        self,
        request: Request,
        path: list[str],
    ) -> Optional[Response | Node]:
        if not self.default_page:
            raise NotFound
        return await awaitable(self.default_page())


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


def router_from_root_package_name(package_name: str) -> Router:
    module = import_module(package_name)
    assert hasattr(module, '__path__')
    path_str = module.__path__[0]
    path = Path(path_str)
    return Router(path, package_name)


class NotFound(Exception):
    pass