from types import ModuleType
from typing import Mapping
from blu._utils.typing import Callable
from importlib import import_module
import inspect
from inspect import Parameter
from pathlib import Path
from blu._utils.typing import Any, Optional, Protocol
from blu._http import Request, Response
from blu._nodes import Node
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
            if path.name == '__index__.py':
                self.index_page = self._get_page_handler(full_name)
            elif path.name == '__default__.py':
                self.default_page = self._get_page_handler(full_name)
            elif is_static_segment(path):
                self.static_segments[name] = Router(path, full_name)
            elif is_dynamic_segment(path):
                nunder = name.strip('_')
                self.dynamic_segments[nunder] = Router(path, full_name)

    def _get_page_handler(self, module_name: str) -> Handler:
        module = import_module(module_name)
        return module.__page__
    
    async def handle(self, request: Request) -> Response:
        path = request.path
        stripped = path.strip('/')
        segments: list[str] = [] if stripped == '' else stripped.split('/')
        response = await self.handle_rec(request, segments)
        assert response is not None
        return response

    async def handle_rec(
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
        args = self._get_handler_args(
            self.index_page,
            path,
            route_params,
        )
        kwargs = self._get_handler_kwargs(
            self.index_page,
            route_params,
            request,
            path,
        )
        return await awaitable(self.index_page(*args, **kwargs))
    
    def _get_handler_kwargs[**P](
        self,
        handler: Callable[P, Response | Node],
        route_params: dict[str, str],
        request: Request,
        path: list[str],
    ) -> dict[str, Any]:
        fn_params = inspect.signature(handler).parameters
        if any(p.kind is p.POSITIONAL_ONLY for p in fn_params.values()):
            if any(p.kind is p.VAR_KEYWORD for p in fn_params.values()):
                return {
                    name: query_list[0]
                    for name, query_list in request.query
                }
            else:
                ret = {}
                for p in fn_params.values():
                    if p.kind is p.POSITIONAL_ONLY:
                        continue
                    value = request.query.get(p.name, p.default)
                    if value is Parameter.empty:
                       raise TypeError(
                            f'Unable to process query parameter {p.name} for '
                            f'URL path {request.path}: __page__ handler has '
                            f'no argument named "{p.name}".'
                        )
                    ret[p.name] = value
                return ret
        ret: dict[str, Any] = {}
        for fn_param in fn_params.values():
            if fn_param.name == '_':
                ret['_'] = None
            elif fn_param.name.endswith('__'):
                ret[fn_param.name] = '/'.join(path)
            else:
                try:
                    ret[fn_param.name] = route_params[fn_param.name]
                except KeyError:
                    raise TypeError(
                        f'__page__ handler {handler} has route '
                        f'argument "{fn_param.name}", which does not '
                        'exist for this route (URL path: '
                        f'{request.path}).'
                    )
        return ret

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
                response = await segment.handle_rec(
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
            try:
                response = await segment.handle_rec(
                    request,
                    path[1:],
                    new_route_params,
                )
            except NotFound:
                continue
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
        args = self._get_handler_args(
            self.default_page,
            path,
            route_params,
        )
        kwargs = self._get_handler_kwargs(
            self.default_page,
            route_params,
            request,
            path,
        )
        return await awaitable(self.default_page(*args, **kwargs))
    
    def _get_handler_args[**P](
        self,
        default_handler: Callable[P, Response | Node],
        path: list[str],
        route_params: Mapping[str, str],
    ) -> tuple[Any, ...]:
        parameters = inspect.signature(default_handler).parameters
        ret: tuple[Any, ...] = ()
        for p in parameters.values():
            if p.kind is not Parameter.POSITIONAL_ONLY:
                break
            if p.name == '_':
                ret += (None,)
            elif p.name.endswith('__'):
                ret += ('/'.join(path),)
            else:
                ret += (route_params[p.name],)
        return ret


def is_static_segment(path: Path) -> bool:
    name = path.stem
    return (
        path.is_dir() and
        len(name) > 0 and
        name[0] != '_' and
        name[-1] != '_'
    )


def is_dynamic_segment(path: Path) -> bool:
    name = path.stem
    return (
        path.is_dir() and
        len(name) > 2 and
        name[0] == '_' and
        name[1] != '_' and
        name[-1] == '_' and
        name[-2] != '_'
    )


def router_from_root_package(module: ModuleType) -> Router:
    assert hasattr(module, '__path__')
    path_str = module.__path__[0]
    path = Path(path_str)
    return Router(path, module.__name__)


class NotFound(Exception):
    pass