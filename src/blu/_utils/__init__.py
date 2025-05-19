from pathlib import Path
from . import typing
from blu._utils.client import client

from blu._utils.asyncio import io_bound

if typing.TYPE_CHECKING:
    from blu._app import Blu

if not client:
    import shutil
    import socket


def get_available_port() -> int:
    s = socket.socket()  # type: ignore
    s.bind(('', 0))
    return s.getsockname()[1]


@io_bound
def copy_file(src: Path, dest: Path):
    shutil.copyfile(src, dest)  # type: ignore


@io_bound
def copy_tree(src: Path, dest: Path):
    shutil.copytree(src, dest)  # type: ignore


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