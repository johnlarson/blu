from collections import defaultdict
from importlib import import_module
from io import StringIO
import json
import os
from collections.abc import Iterable
from numbers import Number
from pathlib import Path
from typing import Optional, Protocol, TypedDict, cast
from xml.etree import ElementTree as ET

from blu._app.Settings import ImportMap
from blu._context import DependencyMapJSONContext
from blu._utils import io_bound, parse_json, serialize_json
from blu._react._render.react_data import get_react_data
from blu._react._types import (
    Jsonable, Node, PropValue, CustomElement, HTMLElement, is_node
)

js_root = Path(__file__).parent.parent / 'js'

with open(js_root / 'dynamic-import-replacement.js', 'r') as d_i_r_f:
    dynamic_import_replacement_content = d_i_r_f.read()

with open(js_root / 'bootstrap-script.js', 'r') as bootstrap_script_f:
    bootstrap_script_content = bootstrap_script_f.read()


type Renamer = dict[tuple[Optional[str], Path], Optional[str]]


class Renderer:
    _react_location: str
    _react_dom_location: str
    _root_dir: Path
    _dependency_map: Optional[dict[str, list[str]]]
    _dependency_map_json: Optional[str]
    _importmap: ImportMap
    
    def __init__(
        self,
        react_location: str = 'https://esm.sh/react',
        react_dom_location: str = 'https://esm.sh/react-dom',
        root_dir: Optional[Path | str] = None,
        dependency_map: Optional[dict[str, list[str]]] = None,
        dependency_map_json: Optional[str] = None,
        importmap: Optional[ImportMap] = None,
    ):
        if root_dir is None:
            root_dir = os.getcwd()
        if importmap is None:
            importmap = {}
        
        self._react_location = react_location
        self._react_dom_location = react_dom_location
        self._root_dir = Path(root_dir)
        self._dependency_map = dependency_map
        self._dependency_map_json = dependency_map_json
        self._importmap = importmap
    
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
        if self._dependency_map_json is not None:
            document.append(self._get_dependency_map())
        document.extend([
            await self._get_react_data(root),
            await self._get_importmap(),
            self._get_dynamic_import_replacement(),
            self._get_script_tag(root),
        ])
        return document

    def _get_placeholder(self) -> ET.Element:
        html = ET.Element('html')
        html.append(ET.Element('head'))
        html.append(ET.Element('body'))
        return html

    def _get_dependency_map(self) -> ET.Element:
        assert self._dependency_map_json is not None
        element = ET.Element('script', {'type': 'dependency-map'})
        element.text = self._dependency_map_json
        return element
    
    async def _get_react_data(self, root: Node) -> ET.Element:
        react_data = get_react_data(root)
        react_data_str = await serialize_json(react_data)
        element = ET.Element('script', type='react-data')
        element.text = react_data_str
        return element

    async def _get_importmap(self) -> ET.Element:
        element = ET.Element('script', {'type': 'importmap'})
        element.text = await serialize_json(self._importmap)
        return element

    def _get_dynamic_import_replacement(self) -> ET.Element:
        element = ET.Element('script')
        element.text = dynamic_import_replacement_content
        return element

    def _get_script_tag(self, root: Node) -> ET.Element:
        element = ET.Element('script', {'type': 'module'})
        element.text = bootstrap_script_content
        return element

    def _get_bootstrap_script(self, root: Node) -> str:
        renamer = self._get_import_data(root)
        imports = self._get_bootstrap_script_imports(renamer)
        code = self._get_bootstrap_script_code(root, renamer)
        return imports + code

    def _get_bootstrap_script_imports(self, renamer: Renamer) -> str:
        r_module = self._react_location
        ce_import = f"import {{ createElement }} from '{r_module}';"
        rd_module = self._react_dom_location
        cr_import = f"import {{ createRoot }} from '{rd_module}';"
        component_imports = self._get_component_imports(renamer)
        return ce_import + cr_import + component_imports
    
    def _get_component_imports(self, renamer: Renamer) -> str:
        ret = ''
        for k, rename in renamer.items():
            src_name, path = k
            ret += self._get_component_import(src_name, rename, path)
        return ret
    
    def _get_component_import(
        self, src_name: Optional[str], rename: Optional[str], path: Path
    ) -> str:
        return f'import {{ {src_name} as {rename} }} from "{path}.js";'
    
    def _get_import_data(self, root: Node) -> Renamer:
        components = self._get_custom_elements(root)
        name_counts: dict[str, int] = defaultdict(lambda: 0)
        ret: dict[tuple[Optional[str], Path], Optional[str]] = {}
        for el in components:
            desired_name = 'Default' if el.name == 'default' else el.name
            count = name_counts[desired_name]
            if count:
                rename = f'{desired_name}{count + 1}'
            else:
                rename = desired_name
            name_counts[desired_name] += 1
            ret[(el.name, el.path)] = rename
        return ret
    
    def _flatten_dependencies(self, importer: str) -> set[str]:
        if self._dependency_map is None:
            return set()
        immediate_deps = self._dependency_map[importer]
        dependencies = set(immediate_deps)
        for dep in immediate_deps:
            dependencies = dependencies | self._flatten_dependencies(dep)
        return dependencies

    def _get_custom_elements(self, root: Node) -> list[CustomElement]:
        if isinstance(root, (HTMLElement, CustomElement)):
            found = [self._get_custom_elements(x) for x in root.children]
            found_flat = [item for itemlist in found for item in itemlist]
            if isinstance(root, CustomElement):
                return [root, *found_flat]
            else:
                return found_flat
        return []
    
    def _get_bootstrap_script_code(self, root: Node, renamer: Renamer) -> str:
        start = 'createRoot(document).render('
        root_node_code = self._render_node_to_js(root, renamer)
        end = ');'
        return start + root_node_code + end
    
    def _render_node_to_js(self, node: Node, renamer: Renamer) -> str:
        if node is None:
            return 'null'
        elif node is True:
            return 'true'
        elif node is False:
            return 'false'
        elif isinstance(node, Number):
            return str(node)
        elif isinstance(node, str):
            return json.dumps(node)
        elif isinstance(node, HTMLElement):
            return self._render_html_element_to_js(node, renamer)
        elif isinstance(node, CustomElement):
            return self._render_custom_element_to_js(node, renamer)
        elif isinstance(node, Iterable):
            return self._render_iterable_to_js(node, renamer)
        else:
            raise TypeError('Can only render HTMLElement objects.')
        
    def _render_custom_element_to_js(
        self, element: CustomElement, renamer: Renamer
    ) -> str:
        rename = renamer[(element.name, element.path)]
        if rename is None:
            name = element.name
        else:
            name = rename
        return self._render_element_to_js(name, element, renamer)
    
    def _render_html_element_to_js(
        self, element: HTMLElement, renamer: Renamer
    ) -> str:
        return self._render_element_to_js(
            f'\'{element.tagname}\'', element, renamer
        )
    
    def _render_element_to_js(
        self,
        type_js: str,
        element: CustomElement | HTMLElement,
        renamer: Renamer,
    ) -> str:
        start = 'createElement('
        type = f'{type_js},'
        props = f'{self._render_props(element, renamer)},'
        children = self._render_comma_separated(element.children, renamer)
        end = ')'
        return start + type + props + children + end
    
    def _render_props(
        self, element: HTMLElement | CustomElement, renamer: Renamer
    ) -> str:
        start = '{'
        props_rendered = [
            f'{json.dumps(k)}:{self._render_prop_value(v, renamer)}'
            for k, v in element.props.items()
        ]
        props = ','.join(props_rendered)
        end = '}'
        return start + props + end

    def _render_prop_value(self, value: PropValue, renamer: Renamer) -> str:
        if is_node(value):
            node = cast(Node, value)
            return self._render_node_to_js(node, renamer)
        else:
            data = cast(Jsonable, value)
            return json.dumps(data)
    
    def _render_comma_separated(
            self, children: Iterable[Node], renamer: Renamer) -> str:
        children_render_list = [
            self._render_node_to_js(x, renamer) for x in children
        ]
        return ','.join(children_render_list)
    
    def _render_iterable_to_js(
        self, iterable: Iterable[Node], renamer: Renamer
    ) -> str:
        start = '['
        items = self._render_comma_separated(iterable, renamer)
        end = ']'
        return start + items + end