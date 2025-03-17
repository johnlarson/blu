from pathlib import Path
from typing import Optional

from blu._utils import copy_file, json


async def copy_static_file(src_path: Path, src_root: Path, dest_root: Path):
    if src_path.suffix == 'py':
        return
    rel_path = src_path.relative_to(src_root)
    dest_path = dest_root / rel_path
    copy_file(src_path, dest_path)


class FileBuildProcessor:
    src_root: Path
    dest_root: Path

    def __init__(self, src_root: Path, dest_root: Path):
        self.src_root = src_root.resolve()
        self.dest_root = dest_root.resolve()
    
    async def copy_file(self, src: Path):
        if src.suffix == 'py':
            return
        rel_path = src.relative_to(self.src_root)
        dest = self.dest_root / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        await copy_file(src, dest)