from io import StringIO
import os
from pathlib import Path
from typing import Optional
from xml.etree import ElementTree as ET

from blu._utils import json
from blu._react._render.react_data import get_react_data
from blu._react.types import Node

js_root = Path(__file__).parent.parent / 'js'

with open(js_root / 'bootstrap-script.js', 'r') as bootstrap_script_f:
    bootstrap_script_content = bootstrap_script_f.read()


type Renamer = dict[tuple[Optional[str], Path], Optional[str]]


class Renderer:
    _react_location: str
    _react_dom_location: str
    _root_dir: Path
    
    def __init__(
        self,
        react_location: str = 'https://esm.sh/react',
        react_dom_location: str = 'https://esm.sh/react-dom',
        root_dir: Optional[Path | str] = None,
    ):
        if root_dir is None:
            root_dir = os.getcwd()
        
        self._react_location = react_location
        self._react_dom_location = react_dom_location
        self._root_dir = Path(root_dir)
    
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
            self._get_script_tag(root),
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

    def _get_script_tag(self, root: Node) -> ET.Element:
        element = ET.Element('script', {'type': 'module'})
        element.text = bootstrap_script_content
        return element
