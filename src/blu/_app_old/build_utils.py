from pathlib import Path

from blu._utils import copy_file, copy_tree, blu_package_root, ensure_dir


class FileBuildProcessor:
    src_root: Path
    dest_root: Path

    def __init__(self, src_root: Path, dest_root: Path):
        self.src_root = src_root.resolve()
        self.dest_root = dest_root.resolve()

    async def copy_blu_lib(self):
        src = blu_package_root
        blu_internal = self.dest_root / '_blu_internal'
        dest = blu_internal / 'python_path' / 'blu'
        await ensure_dir(blu_internal)
        await copy_tree(src, dest)
    
    async def build_file(self, src: Path):
        if src.suffix == '.py':
            await self._build_python_file(src)
        else:
            await self._copy_file(src)
        
    async def _build_python_file(self, src: Path):
        client_python_path = self.dest_root / '_blu_internal/python_path/app'
        dest = client_python_path / self._relative(src)
        await self._copy(src, dest)

    async def _copy_file(self, src: Path):
        rel_path = self._relative(src)
        dest = self.dest_root / rel_path
        await self._copy(src, dest)
    
    def _relative(self, src_path: Path) -> Path:
        return src_path.relative_to(self.src_root)
    
    async def _copy(self, src: Path, dest: Path):
        dest.parent.mkdir(parents=True, exist_ok=True)
        await copy_file(src, dest)