print('Hello, World!')

import base64
from collections import defaultdict
import pickle
from blu._utils.typing import Generator

print('defaultdic:', defaultdict)


print('Generator:', Generator)


import asyncio
from collections.abc import AsyncGenerator, Callable, Generator, Sequence
import importlib
from typing import Any, Protocol, TypedDict, cast
from xml.dom.minidom import Element

from blu._core._render.react_data import ClientElementDict, ReactDict, ReactJsObject
from js import alert, console, document  # type: ignore
import json
from pyscript import js_import  # type: ignore
from pyscript.ffi import create_proxy, to_js  # type: ignore

from blu._nodes import ElementRenderer, ClientElement, HTMLElement, Jsonable, Node, Key

# react_dom = await js_import('https://esm.sh/react-dom/client')
# react = await js_import('https://esm.sh/react')

from pyscript.js_modules import _blu_react_dom as react_dom
from pyscript.js_modules import _blu_react as react


async def main():
    b64_str: str = cast(str, document.querySelector('script[type="react-data"]').textContent)  # type: ignore
    b64_bytes = b64_str.encode('ascii')
    pickled = base64.b64decode(b64_bytes)
    unpickled = pickle.loads(pickled)
    root_node = get_node(unpickled)
    if root_node_json['tagname'] == 'html':
        react_dom.createRoot(document).render(root_node)
    else:
        react_dom.createRoot(document.body).render(root_node)  # type: ignore


def get_node(data: Any):
    print('DATA:', data)
    if isinstance(data, list):
        return get_array(data)
    elif isinstance(data, ClientElement):
        return py_to_js_node(data)
    elif isinstance(data, Key):
        props = {'key': data['key']}
        return react.createElement(
            react.Fragment,
            {'key': data._key},
            *get_array(data._children),
        )
    elif isinstance(data, tuple):
        return react.createElement(
            react.Fragment,
            {},
            *get_array(data),
        )
    elif isinstance(data, HTMLElement):
        return react.createElement(
            data._tagname,
            data._props,
            *get_array(data['children']),
        )
    else:
        return data


def get_obj(obj: ReactJsObject):
    return {k: get_node(v) for k, v in obj.items()}


def get_dict(my_dict: dict):
    return {k: get_node(v) for k, v in my_dict.items()}


def get_array_old(array: Any):
    return [get_node(x) for x in array]


class PythonElementProps(TypedDict):
    renderer: ElementRenderer
    args: tuple[Jsonable, ...]
    kwargs: dict[str, Jsonable]
    py_children: list[Node]


@create_proxy
def PythonElement(props: PythonElementProps, extra: Any = None):
    print('A')
    result = props.renderer(*props.args, **props.kwargs.as_object_map())
    print('B')
    if isinstance(result, Generator):
        next(result)
        result.send(props.py_children)
        try:
            next(result)
        except StopIteration as e:
            return py_to_js_node(e.value)
    elif isinstance(result, AsyncGenerator):
        raise TypeError('ClientElements cannot be created from async rendering functions.')
    else:
        ret = py_to_js_node(result)
        console.log('RET:', ret)
        return ret
        # return py_to_js_node(result)


def py_to_js_node(py_node: Node):
    print('PY NODE:', py_node)
    if isinstance(py_node, ClientElement):
        console.log('RENDERER?', py_node, py_node.renderer)
        return react.createElement(
            PythonElement,
            to_js({
                'renderer': create_proxy(py_node.renderer),
                'args': py_node.args,
                'kwargs': py_node.kwargs,
                'py_children': py_node.children,
            }),
        )
    elif isinstance(py_node, HTMLElement):
        return react.createElement(
            py_node.tagname,
            to_js({
                k: create_proxy(v) if k.startswith('on') else v
                for k, v in py_node.props.items()
            }),
            *py_node.children,
        )


def parse_py_element(data: ClientElementDict):
    print('CLIENT ELEMENT:', data)
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