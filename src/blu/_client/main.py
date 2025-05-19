print('Hello, World!')

from collections import defaultdict
from blu._utils.typing import Generator

print('defaultdic:', defaultdict)


print('Generator:', Generator)


import asyncio
from collections.abc import AsyncGenerator, Callable, Generator, Sequence
import importlib
from typing import Any, Protocol, TypedDict, cast
from xml.dom.minidom import Element

from blu._react._render.react_data import ClientElementDict, ReactDict, ReactJsObject
from js import document  # type: ignore
import json
from pyscript import js_import  # type: ignore

from blu._react.types import ElementRenderer, ClientElement, Jsonable, Node

# react_dom = await js_import('https://esm.sh/react-dom/client')
# react = await js_import('https://esm.sh/react')

from pyscript.js_modules import _blu_react_dom as react_dom
from pyscript.js_modules import _blu_react as react

async def main():
    json_str = document.querySelector('script[type="react-data"]').textContent  # type: ignore
    root_node_json = json.loads(json_str)  # type: ignore
    root_node = get_node(root_node_json)
    # import_promises = get_import_promises(root_node_json)
    # imports = await asyncio.gather(import_promises)
    # root_node = get_node(root_node_json, imports)
    if root_node_json['tagname'] == 'html':
        react_dom.createRoot(document).render(root_node)
    else:
        react_dom.createRoot(document.body).render(root_node)  # type: ignore


def get_node(data: Any):
    if isinstance(data, list):
        return get_array(data)
    elif isinstance(data, dict):
        data = cast(ReactDict, data)
        if 'type' not in data:
            raise TypeError('Data dict should have key "type"')
        elif data['type'] == 'object':
            return get_obj(data)
        elif data['type'] == 'client_element':
            py_element = parse_py_element(data)
            return py_to_js_node(py_element)
        elif data['type'] == 'fragment':
            props = {'key': data['key']} if 'key' in data else {}
            return react.createElement(react.Fragment, get_obj(props))
        elif data['type'] == 'native_element':
            return react.createElement(
                data['tagname'],
                get_obj(data['props']),
                *get_array(data['children']),
            )
        else:
            raise TypeError(f'Unknown ReactDict type: "{data['type']}"')
    else:
        return data


def get_obj(obj: ReactJsObject):
    print('OBJ:', obj)
    return {k: get_node(v) for k, v in obj['data'].items()}


def get_array(array: Any):
    [get_node(x) for x in array]


class PythonElementProps(TypedDict):
    renderer: ElementRenderer
    args: tuple[Jsonable, ...]
    kwargs: dict[str, Jsonable]
    py_children: list[Node]


def PythonElement(props: PythonElementProps):
    result = props['renderer'](*props['args'], children=props['py_children'], **props['kwargs'])
    if isinstance(result, Generator):
        next(result)
        result.send(props['py_children'])
        try:
            next(result)
        except StopIteration as e:
            return py_to_js_node(e.value)
    elif isinstance(result, AsyncGenerator):
        raise TypeError('ClientElements cannot be created from async rendering functions.')
    else:
        return py_to_js_node(result)


def py_to_js_node(py_node: Node):
    if isinstance(py_node, ClientElement):
        return react.createElement(
            PythonElement,
            {
                'renderer': py_node.renderer,
                'args': py_node.args,
                'kwargs': py_node.kwargs,
                'py_children': py_node.children,
            },
        )


def parse_py_element(data: ClientElementDict):
    return ClientElement(
        get_renderer(data),
        get_array(data['args']),
        get_obj(data['kwargs']),
        get_node(data['children']),
    )


def get_renderer(data: Any) -> ElementRenderer:
    module = importlib.import_module(data['module'])
    return getattr(module, data['name'])


await main()