from pathlib import Path

from blu._app.build_utils import copy_static_file
from blu._utils import walk_dir_files


async def build(app_root: Path, static_out: Path):
    for path in await walk_dir_files(app_root):
        await copy_static_file(path, app_root, static_out)