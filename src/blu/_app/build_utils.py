from pathlib import Path

from blu._utils import copy_file


async def copy_static_file(src_path: Path, src_root: Path, dest_root: Path):
    if src_path.suffix == 'py':
        return
    rel_path = src_path.relative_to(src_root)
    dest_path = dest_root / rel_path
    copy_file(src_path, dest_path)