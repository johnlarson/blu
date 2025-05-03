import asyncio
from collections.abc import AsyncGenerator, Callable, Coroutine
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, cast

from watchdog.events import DirCreatedEvent, DirModifiedEvent, DirMovedEvent, FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent, FileMovedEvent
from watchdog.observers import Observer

from blu._app.build_utils import FileBuildProcessor


@asynccontextmanager
async def watch_build(
    app_dir: Path,
    static_dir: Path,
    build_dir: Path,
) -> AsyncGenerator[None]:
    build_dir.mkdir()
    async with watch_copy(app_dir, static_dir):
        yield


@asynccontextmanager
async def _watch(
    src: Path,
    handler: Callable[[Path], Coroutine[None, Any, Any]]
) -> AsyncGenerator[None, None]:
    event_handler = WatchEventHandler(handler)
    observer = Observer()
    observer.schedule(event_handler, str(src), recursive=True)
    observer.start()
    try:
        yield
    finally:
        observer.stop()
        observer.join()


@asynccontextmanager
async def watch_copy(src: Path, dest: Path) -> AsyncGenerator[None, None]:
    processor = FileBuildProcessor(src, dest)
    async with _watch(src, processor.build_file):
        yield


class WatchEventHandler(FileSystemEventHandler):
    _handler: Callable[[Path], Coroutine[None, Any, Any]]

    def __init__(self, handler: Callable[[Path], Coroutine[None, Any, Any]]):
        super().__init__()
        self._handler = handler
    
    def on_created(self, event: FileCreatedEvent | DirCreatedEvent):  # type: ignore
        if isinstance(event, FileCreatedEvent):
            self._handle_file(event.src_path)

    def on_modified(self, event: FileModifiedEvent | DirModifiedEvent):  # type: ignore
        if isinstance(event, FileModifiedEvent):
            self._handle_file(event.src_path)

    def on_moved(self, event: FileMovedEvent | DirMovedEvent):  # type: ignore
        if isinstance(event, FileMovedEvent):
            self._handle_file(event.dest_path)

    def _handle_file(self, src_path_str: str | bytes):
        if isinstance(src_path_str, bytes):
            src_path_str = src_path_str.decode()
        src_path_str = cast(str, src_path_str)
        # if src_path_str.startswith('/private'):
        #     src_path_str = src_path_str[8:]
        src = Path(src_path_str)
        asyncio.run(self._handler(src))