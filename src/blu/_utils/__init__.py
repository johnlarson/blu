import base64
from pathlib import Path

from blu._utils.asyncio import io_bound
from blu._utils.client import is_client
from blu._micropython.typing import Any, cast

from blu.mPickle import mpickle as pickle

if not is_client:
    import shutil
    import socket


def get_available_port() -> int:
    s = socket.socket()  # type: ignore
    s.bind(("", 0))
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


def unpickle_root() -> Any:
    from js import document  # type: ignore

    b64_str_uncast = document.querySelector('script[type="react-data"]').textContent  # type: ignore
    b64_str: str = cast(str, b64_str_uncast)
    b64_bytes = b64_str.encode("ascii")
    pickled = base64.b64decode(b64_bytes)
    return pickle.loads(pickled)  # type: ignore


blu_package_root = Path(__file__).parent.parent
