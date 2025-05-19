from io import StringIO
import os
from pathlib import Path
from blu._utils.typing import Optional
from xml.etree import ElementTree as ET

from blu._utils import json, walk_dir_files
from blu._react._render.react_data import get_react_data
from blu._react.types import Jsonable, Node

js_root = Path(__file__).parent.parent / 'js'

# with open(js_root / 'bootstrap-script.js', 'r') as bootstrap_script_f:
#     bootstrap_script_content = bootstrap_script_f.read()

py_bootstrap_path = Path(__file__).parent / 'bootstrap_script.py'

# with open(py_bootstrap_path, 'r') as py_bootstrap_f:
#     py_bootstrap_content = py_bootstrap_f.read()


type Renamer = dict[tuple[Optional[str], Path], Optional[str]]


class Renderer:
    _react_location: str
    _react_dom_location: str
    _static_dir: Path

    @property
    def _python_path(self):
        return self._static_dir / '_blu_internal/python_path'
    
    def __init__(
        self,
        static_dir: Path | str,
        react_location: str = 'https://esm.sh/react',
        react_dom_location: str = 'https://esm.sh/react-dom',
    ):
        self._react_location = react_location
        self._react_dom_location = react_dom_location
        self._static_dir = Path(static_dir)
    
    async def render_to_str(self, root: Node) -> str:
        """
        Render the given `ReactElement` to a `str`.

        :param root: The `ReactElement` to render.

        :returns: An html page as a `str`, with `root` rendered as html,
        as well as the bootstrapping code to hydrate the page.
        """
        tree = await self._get_tree(root)
        output = StringIO()
        tree.write(output, encoding='unicode', method='html')
        output_str = output.getvalue()
        start = len('<document>')
        end = -len('</document>')
        no_root = output_str[start:end]
        with_doc_type = '<!DOCTYPE html>' + no_root
        return with_doc_type

    async def _get_tree(self, root: Node) -> ET.ElementTree:
        return ET.ElementTree(await self._get_document(root))

    async def _get_document(self, root: Node) -> ET.Element:
        document = ET.Element('document')
        document.append(self._get_placeholder())
        document.extend([
            await self._get_react_data(root),
            # self._get_script_tag(root),
            self._get_pyscript_include(),
            await self._get_python_script(),
        ])
        return document

    def _get_placeholder(self) -> ET.Element:
        html = ET.Element('html')
        html.append(ET.Element('head'))
        html.append(ET.Element('body'))
        return html

    
    async def _get_react_data(self, root: Node) -> ET.Element:
        react_data = get_react_data(root)
        react_data_str = await json.dumps(react_data)
        element = ET.Element('script', type='react-data')
        element.text = react_data_str
        return element

    # def _get_script_tag(self, root: Node) -> ET.Element:
    #     element = ET.Element('script', {'type': 'module'})
    #     element.text = bootstrap_script_content
    #     return element

    def _get_pyscript_include(self) -> ET.Element:
        return ET.Element(
            'script',
            {
                'type': 'module',
                'src': 'https://pyscript.net/releases/2025.3.1/core.js',
            },
        )

    async def _get_python_script(self) -> ET.Element:
        file_paths = await self._gather_python_files()
        config: dict[str, Jsonable] = {
            'files': {
                str(Path('/_blu_internal/python_path/') / file_path): './' + str(file_path)
                for file_path in file_paths
            },
            'js_modules': {
                'main': {
                    'https://esm.sh/react-dom/client': '_blu_react_dom',
                    'https://esm.sh/react': '_blu_react',
                },
            },
            # 'packages': ['typing'],
            # 'packages': ['github:josverl/micropython-stubs/mip/typing.py'],

        }
        return ET.Element(
            'script',
            {
                'type': 'py',
                'config': await json.dumps(config),
                'src': '/_blu_internal/python_path/blu/_client/main.py',
            },
        )
    
    async def _gather_python_files(self) -> list[Path]:
        return [
            x.relative_to(self._python_path)
            for x in await walk_dir_files(self._python_path)
            if x.suffix == '.py'
        ]