from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import socket
import typing

if typing.TYPE_CHECKING:
    from blu._app import Blu


def get_available_port() -> int:
    s = socket.socket()
    s.bind(('', 0))
    return s.getsockname()[1]


@asynccontextmanager
async def watch_dev_app(app: 'Blu') -> AsyncGenerator[None]:
    ...