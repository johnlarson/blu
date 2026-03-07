import ast
import base64
from functools import cache
from io import StringIO
from pathlib import Path
import pickle
import shutil
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from blu._settings import settings
from blu._utils.typing import Optional
from xml.etree import ElementTree as ET

from blu._nodes import Jsonable, Node
from blu._utils import json

type Renamer = dict[tuple[Optional[str], Path], Optional[str]]

REACT_LOCATION = "https://esm.sh/react"
REACT_DOM_LOCATION = "https://esm.sh/react-dom"
PYSCRIPT_URL = "https://pyscript.net/releases/2026.1.1/core.js"


async def render_to_str(root: Node) -> str:
    """
    Render the given `ReactElement` to a `str`.

    :param root: The `ReactElement` to render.

    :returns: An html page as a `str`, with `root` rendered as html,
    as well as the bootstrapping code to hydrate the page.
    """
    tree = await _get_tree(root)
    output = StringIO()
    tree.write(output, encoding="unicode", method="html")
    output_str = output.getvalue()
    start = len("<document>")
    end = -len("</document>")
    no_root = output_str[start:end]
    with_doc_type = "<!DOCTYPE html>" + no_root
    return with_doc_type


async def _get_tree(root: Node) -> ET.ElementTree:
    return ET.ElementTree(await _get_document(root))


async def _get_document(root: Node) -> ET.Element:
    document = ET.Element("document")
    document.append(_get_placeholder())
    document.extend(
        [
            await _get_react_data(root),
            _get_pyscript_include(),
            await _get_python_script(),
        ]
    )
    return document


def _get_placeholder() -> ET.Element:
    html = ET.Element("html")
    html.append(ET.Element("head"))
    html.append(ET.Element("body"))
    return html


async def _get_react_data(root: Node) -> ET.Element:
    pickled = pickle.dumps(root)
    b64 = base64.b64encode(pickled).decode("ascii")
    element = ET.Element("script", type="react-data")
    element.text = b64
    return element


def _get_pyscript_include() -> ET.Element:
    return ET.Element(
        "script",
        {
            "type": "module",
            "src": PYSCRIPT_URL,
        },
    )


async def _get_python_script() -> ET.Element:
    return ET.Element(
        "script",
        {
            "type": "py",
            "config": await json.dumps(await _get_config()),
            "src": "/_blu_internal/client_main.py",
        },
    )


async def _get_config() -> dict[str, Jsonable]:
    return {
        "js_modules": {
            "main": {
                "https://esm.sh/react-dom/client": "_blu_react_dom",
                "https://esm.sh/react": "_blu_react",
                "/_blu_internal/util.js": "_blu_js_utils",
            },
        },
        "debug": True,
        "files": {
            "/_blu_internal/blu_pkg.zip": "./blu/*",
            "/_blu_internal/app_pkg.zip": "./app/*",
        },
        "packages": settings().CLIENT_REQUIREMENTS,
    }
