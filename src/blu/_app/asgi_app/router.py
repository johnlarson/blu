from collections.abc import Callable
from importlib import import_module
import inspect
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
    dynamic_segments: dict[str, 'Router']

    def __init__(self, dir: Path, package_name: str):
        self.index_page = None
        self.default_page = None
        self.static_segments = {}
        self.dynamic_segments = {}
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
                nunder = name.strip('_')
                self.dynamic_segments[nunder] = Router(path, full_name)

    def _get_page_handler(self, module_name: str) -> Handler:
        module = import_module(module_name)
        return module.__page__

    async def handle(
        self,
        request: Request,
        path: list[str],
        route_params: dict[str, str] = {},
    ) -> Optional[Response]:
        response_ret = await self._get_handler_ret(request, path, route_params)
        if isinstance(response_ret, Response):
            return response_ret
        else:
            return Response(response_ret)
        
    async def _get_handler_ret(
        self,
        request: Request,
        path: list[str],
        route_params: dict[str, str],
    ) -> Response | Node:
        try:
            return await self._handle_index_page(request, path, route_params)
        except NotFound:
            pass
        try:
            return await self._handle_static(request, path, route_params)
        except NotFound:
            pass
        try:
            return await self._handle_dynamic(request, path, route_params)
        except NotFound:
            pass
        return await self._handle_default_page(request, path, route_params)
        
    async def _handle_index_page(
        self,
        request: Request,
        path: list[str],
        route_params: dict[str, str],
    ) -> Response | Node:
        if not self.index_page:
            raise NotFound
        if path:
            raise NotFound
        kwargs = self._get_handler_kwargs(self.index_page, route_params)
        return await awaitable(self.index_page(**kwargs))
    
    def _get_handler_kwargs[**P](
        self,
        handler: Callable[P, Response | Node],
        route_params: dict[str, str],
    ) -> dict[str, str]:
        signature = inspect.signature(handler)
        return {
            fn_param.name: route_params[fn_param.name]
            for fn_param in signature.parameters.values()
            if fn_param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
        }

    async def _handle_static(
        self,
        request: Request,
        path: list[str],
        route_params: dict[str, str],
    ) -> Response | Node:
        if not path:
            raise NotFound
        for name, segment in self.static_segments.items():
            if name == path[0]:
                response = await segment.handle(
                    request,
                    path[1:],
                    route_params,
                )
                if response is not None:
                    return response
        raise NotFound

    async def _handle_dynamic(
        self,
        request: Request,
        path: list[str],
        route_params: dict[str, str],
    ) -> Optional[Response | Node]:
        if not path:
            raise NotFound
        for param_name, segment in self.dynamic_segments.items():
            new_route_params = {**route_params, param_name: path[0]}
            response = await segment.handle(
                request,
                path[1:],
                new_route_params,
            )
            if response is not None:
                return response
        raise NotFound

    async def _handle_default_page(
        self,
        request: Request,
        path: list[str],
        route_params: dict[str, str],
    ) -> Optional[Response | Node]:
        if not self.default_page:
            raise NotFound
        args = self._get_default_handler_args(self.default_page, path)
        kwargs = self._get_handler_kwargs(self.default_page, route_params)
        return await awaitable(self.default_page(*args, **kwargs))
    
    def _get_default_handler_args[**P](
        self,
        default_handler: Callable[P, Response | Node],
        path: list[str],
    ) -> list[str]:
        parameters = inspect.signature(default_handler).parameters
        if len(parameters) >= 1:
            return ['/'.join(path)]
        else:
            return []


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