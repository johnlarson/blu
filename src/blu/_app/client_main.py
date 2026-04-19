print("Hello, World!")

import base64
from collections.abc import AsyncGenerator, Generator, Iterable
import importlib
from importlib import import_module
import logging
import pickle
from typing import Any, TypedDict, cast

from js import console, document  # type: ignore
from pyscript.ffi import create_proxy, to_js  # type: ignore
from pyscript.js_modules import _blu_react as react
from pyscript.js_modules import _blu_js_utils

from blu._nodes import ClientRenderer, ClientElement, HTMLElement, Jsonable, Node, Key
from blu._utils.typing import Generator

logging.basicConfig(level=logging.DEBUG)

PYTHON_TYPES = create_proxy(  # type: ignore
    {
        "ClientElement": ClientElement,
        "Key": Key,
        "tuple": tuple,
        "HTMLElement": HTMLElement,
    }
)


async def main():
    _blu_js_utils.init(import_module)  # type: ignore
    b64_str: str = cast(str, document.querySelector('script[type="react-data"]').textContent)  # type: ignore
    b64_bytes = b64_str.encode("ascii")
    pickled = base64.b64decode(b64_bytes)
    unpickled = pickle.loads(pickled)
    _blu_js_utils.renderRoot(unpickled)  # type: ignore


def get_node(data: Any):
    print("DATA:", data)
    if isinstance(data, ClientElement):
        print("R:", data._renderer)
        print("ARGS:", data._args)
        print("KWARGS:", data._kwargs)
        print("CHILDREN:", data._children)
        return react.createElement(
            PythonElement,
            to_js(
                {
                    "renderer": create_proxy(data._renderer),
                    "args": data._args,
                    "kwargs": data._kwargs,
                    "py_children": data._children,
                }
            ),
        )
    elif isinstance(data, Key):
        props = {"key": data["key"]}
        return react.createElement(
            react.Fragment,
            to_js({"key": data._key}),
            *get_array(data._children),
        )
    elif isinstance(data, tuple):
        return react.createElement(
            react.Fragment,
            to_js({}),
            *get_array(data),
        )
    elif isinstance(data, str):
        return data
    elif isinstance(data, Iterable):
        return get_array(data)
    elif isinstance(data, HTMLElement):
        props = {k: v for k, v in data._attrs.items() if k != "ref"}
        if "ref" in data._attrs.keys():
            props["ref"] = data._attrs["ref"]._js_ref
        return react.createElement(
            data._tagname,
            to_js(props),
            *get_array(data._children),
        )
    elif data is None:
        return None
    else:
        return str(data)


def get_obj(obj: dict[str, Any]):
    return {k: get_node(v) for k, v in obj.items()}


def get_dict(my_dict: dict):
    return {k: get_node(v) for k, v in my_dict.items()}


def get_array(array: Any):
    print("ARRAY:", array)
    return to_js([get_node(x) for x in array])


class PythonElementProps(TypedDict):
    renderer: ClientRenderer
    args: tuple[Jsonable, ...]
    kwargs: dict[str, Jsonable]
    py_children: list[Node]


@create_proxy
def PythonElement(props: PythonElementProps, extra: Any = None):
    print("A")
    result = props.renderer(*props.args, **props.kwargs.as_object_map())
    print("B")
    if isinstance(result, Generator):
        next(result)
        try:
            result.send(props.py_children)
            # next(result)
        except StopIteration as e:
            return get_node(e.value)
    elif isinstance(result, AsyncGenerator):
        raise TypeError(
            "ClientElements cannot be created from async rendering functions."
        )
    else:
        return get_node(result)


def py_to_js_node(py_node: Node):
    print("PY NODE:", py_node)
    if isinstance(py_node, ClientElement):
        console.log("RENDERER?", py_node, py_node.renderer)
        return react.createElement(
            PythonElement,
            to_js(
                {
                    "renderer": create_proxy(py_node.renderer),
                    "args": py_node.args,
                    "kwargs": py_node.kwargs,
                    "py_children": py_node.children,
                }
            ),
        )
    elif isinstance(py_node, HTMLElement):
        return react.createElement(
            py_node.tagname,
            to_js(
                {
                    k: create_proxy(v) if k.startswith("on") else v
                    for k, v in py_node.props.items()
                }
            ),
            *py_node.children,
        )


def parse_py_element(data: dict[str, Any]):
    print("CLIENT ELEMENT:", data)
    return ClientElement(
        get_renderer(data),
        get_array(data["args"]),
        get_obj(data["kwargs"]),
        get_node(data["children"]),
    )


def get_renderer(data: Any) -> ClientRenderer:
    module = importlib.import_module(data["module"])
    return getattr(module, data["name"])


await main()
