from pathlib import Path

from blu._app.build_utils import FileBuildProcessor
from blu._utils import walk_dir_files


async def build(app_root: Path, static_out: Path, build_dir: Path):
    build_dir.mkdir()
    p = FileBuildProcessor(app_root, static_out)
    await p.copy_blu_lib()
    for path in await walk_dir_files(app_root):
        await p.build_file(path)