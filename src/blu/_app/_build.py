from pathlib import Path

from blu._app.build_utils import FileBuildProcessor
from blu._utils import walk_dir_files


async def build(app_root: Path, static_out: Path):
    p = FileBuildProcessor(app_root, static_out)
    for path in await walk_dir_files(app_root):
        await p.copy_file(path)