from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
import shutil
import socket
import typing

from blu._utils.asyncio import io_bound

if typing.TYPE_CHECKING:
    from blu._app import Blu


def get_available_port() -> int:
    s = socket.socket()
    s.bind(('', 0))
    return s.getsockname()[1]


@asynccontextmanager
async def watch_dev_app(app: 'Blu') -> AsyncGenerator[None]:
    ...


@io_bound
def copy_file(src: Path, dest: Path):
    shutil.copyfile(src, dest)


@io_bound
def copy_tree(src: Path, dest: Path):
    shutil.copytree(src, dest)


@io_bound
def ensure_dir(path: Path):
    path.mkdir(exist_ok=True, parents=True)


@io_bound
def list_dir(dir: Path) -> list[Path]:
    return list(dir.iterdir())


@io_bound
def walk_dir_files(dir: Path) -> list[Path]:
    ret: list[Path] = []
    for subdir, _, filenames in dir.walk():
        for filename in filenames:
            file_path = subdir / filename
            ret.append(file_path)
    return ret


blu_package_root = Path(__file__).parent.parent