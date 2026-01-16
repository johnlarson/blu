import base64
from io import StringIO
from pathlib import Path
import pickle
from blu._utils.typing import Optional
from xml.etree import ElementTree as ET

from blu._core.nodes import Jsonable, Node
from blu._utils import json

type Renamer = dict[tuple[Optional[str], Path], Optional[str]]

REACT_LOCATION = 'https://esm.sh/react'
REACT_DOM_LOCATION = 'https://esm.sh/react-dom'
    
    
async def render_to_str(root: Node) -> str:
    """
    Render the given `ReactElement` to a `str`.

    :param root: The `ReactElement` to render.

    :returns: An html page as a `str`, with `root` rendered as html,
    as well as the bootstrapping code to hydrate the page.
    """
    tree = await _get_tree(root)
    output = StringIO()
    tree.write(output, encoding='unicode', method='html')
    output_str = output.getvalue()
    start = len('<document>')
    end = -len('</document>')
    no_root = output_str[start:end]
    with_doc_type = '<!DOCTYPE html>' + no_root
    return with_doc_type

async def _get_tree(root: Node) -> ET.ElementTree:
    return ET.ElementTree(await _get_document(root))

async def _get_document(root: Node) -> ET.Element:
    document = ET.Element('document')
    document.append(_get_placeholder())
    document.extend([
        await _get_react_data(root),
        _get_pyscript_include(),
        await _get_python_script(),
    ])
    return document

def _get_placeholder() -> ET.Element:
    html = ET.Element('html')
    html.append(ET.Element('head'))
    html.append(ET.Element('body'))
    return html

async def _get_react_data(root: Node) -> ET.Element:
    pickled = pickle.dumps(root)
    b64 = base64.b64encode(pickled).decode('ascii')
    element = ET.Element('script', type='react-data')
    element.text = b64
    return element


def _get_pyscript_include() -> ET.Element:
    return ET.Element(
        'script',
        {
            'type': 'module',
            'src': 'https://pyscript.net/releases/2025.3.1/core.js',
        },
    )

async def _get_python_script() -> ET.Element:
    config: dict[str, Jsonable] = {
        'js_modules': {
            'main': {
                'https://esm.sh/react-dom/client': '_blu_react_dom',
                'https://esm.sh/react': '_blu_react',
            },
        },
        'experimental_create_proxy': 'auto',
    }
    return ET.Element(
        'script',
        {
            'type': 'py',
            'config': await json.dumps(config),
            'src': '/blu/_client/main.py',
        },
    )
