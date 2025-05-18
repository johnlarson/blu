from blu._utils.typing import AsyncIterable, AsyncIterator, Mapping
from importlib import import_module
from pathlib import Path
import pkgutil
from types import ModuleType, TracebackType
from blu._utils.typing import Optional
from quart import Quart, Response as QuartResponse
from quart.typing import Headers

from blu._react.types import Node


class Blu(Quart):
    _project_dir: Path

    def __init__(
        self,
        module: ModuleType,
        project_dir: Path | str,
        *,
        debug: Optional[bool] = None,
    ):
        super().__init__('app')
        self._project_dir = Path(project_dir)
        self._add_routes(module, module)
    
    def _add_routes(self, module: ModuleType, root: ModuleType):
        name = module.__name__
        if name.endswith('__index__'):
            self._add_index_route(module, root)
        if hasattr(module, '__path__'):
            for module_info in pkgutil.iter_modules(module.__path__):
                child_name = name + '.' + module_info.name
                child_module = import_module(child_name)
                self._add_routes(child_module, root)

    def _add_index_route(self, module: ModuleType, root: ModuleType):
        relative_to_root = module.__name__[:len(root.__name__)]
        url_path = '/'.join(relative_to_root.split('.'))
        blu_handler = module.__page__
        def quart_handler(**kwargs: str) -> QuartResponse:
            result = blu_handler(**kwargs)
            if isinstance(result, QuartResponse):
                return result
            else:
                return Response(result)
        self.route(url_path)(quart_handler)


class Response(QuartResponse):
    children: Node

    def __init__(
        self,
        children: Node,
        status: Optional[int] = None,
        headers: Mapping[str, str] = {},
    ):
        super().__init__(None, status, Headers(headers))  # type: ignore
        self.children = children


class ReactResponseBody:
    _children: Node

    def __init__(self, children: Node):
        self._children = children
    
    async def __aenter__(self) -> AsyncIterable[AsyncIterator[bytes]]:
        yield get_rendered_bytes(self._children)

    async def __aexit__(
        self,
        exc_type: type,
        exc_value: BaseException,
        tb: TracebackType,
    ):
        pass


async def get_rendered_bytes(node: Node) -> AsyncIterator[bytes]:
    rendered = render_react(node)
    yield rendered.encode('utf-8')


def render_react(node: Node) -> str:
    ...