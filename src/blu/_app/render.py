import base64
from io import StringIO
from pathlib import Path
from xml.etree import ElementTree as ET

from blu._mPickle import mpickle as pickle
from blu._settings import settings
from blu._micropython.typing import Optional
from blu._nodes import Jsonable, Node
from blu._utils import json

type Renamer = dict[tuple[Optional[str], Path], Optional[str]]


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
            await _get_config_script(),
            await _get_react_data(root),
            _get_bootstrap_script(),
        ]
    )
    return document


def _get_bootstrap_script() -> ET.Element:
    interpreter = settings().INTERPRETER
    assert interpreter in ["micropython", "pyodide"]
    if interpreter == "micropython":
        bootstrap_script_name = "micropython-bootstrap.js"
    else:
        bootstrap_script_name = "pyodide-bootstrap.js"
    return ET.Element(
        "script",
        {
            "type": "module",
            "src": f"/_blu_internal/static/{bootstrap_script_name}",
        },
    )


def _get_placeholder() -> ET.Element:
    html = ET.Element("html")
    html.append(ET.Element("head"))
    html.append(ET.Element("body"))
    return html


async def _get_react_data(root: Node) -> ET.Element:
    pickled = pickle.dumps(root)  # type: ignore
    b64 = base64.b64encode(pickled).decode("ascii")
    element = ET.Element("script", type="react-data")
    element.text = b64
    return element


async def _get_config_script() -> ET.Element:
    script = ET.Element(
        "script",
        {
            "type": "json",
            "id": "config",
        },
    )
    script.text = await json.dumps(_get_config())
    return script


def _get_config() -> dict[str, Jsonable]:
    return {
        "packages": settings().CLIENT_REQUIREMENTS,
    }
