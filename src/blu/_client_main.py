import base64

# from importlib import import_module
import logging

# import pickle
from blu.mPickle import mpickle as pickle

import js  # type: ignore

# from pyscript.ffi import create_proxy, to_js  # type: ignore
import _react as react
import _react_dom as react_dom

from blu._nodes import ClientElement, HTMLElement, Key
from blu._micropython.typing import cast
from blu._micropython.utils import is_generator, is_iterable, create_proxy

logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger("blu")

PYTHON_TYPES = create_proxy(  # type: ignore
    {
        "ClientElement": ClientElement,
        "Key": Key,
        "tuple": tuple,
        "HTMLElement": HTMLElement,
    }
)


async def main():
    # _blu_js_utils.init(import_module)  # type: ignore
    b64_str: str = cast(str, js.document.querySelector('script[type="react-data"]').textContent)  # type: ignore
    b64_bytes = b64_str.encode("ascii")
    pickled = base64.b64decode(b64_bytes)
    unpickled = pickle.loads(pickled)
    log.debug(f"Python root node: {unpickled}")

    # _blu_js_utils.renderRoot(unpickled)  # type: ignore
    render_root(unpickled)


def render_root(py_root):
    js_root = get_react_node(py_root)
    log.debug(f"React root node: {js_root}")
    render_target = (
        js.document if getattr(js_root, "type", None) == "html" else js.document.body
    )
    react_dom.createRoot(render_target).render(js_root)


def get_react_node(py_node):
    log.debug(f"Converting python node {repr(py_node)} to React...")
    print("__iter__:", getattr(py_node, "__iter__", None))
    print("is list:", isinstance(py_node, list))
    if isinstance(py_node, ClientElement):
        log.debug("Python node is a ClientElement")
        return react.createElement(
            ReactComponent,
            {
                "renderer": py_node._renderer,
                "args": py_node._args,
                "kwargs": py_node._kwargs,
                "pyChildren": py_node._children,
            },
        )
    elif isinstance(py_node, Key):
        log.debug("Python node is a key.")
        return react.createElement(
            react.Fragment,
            {
                "key": py_node._key,
            },
            *get_array(py_node._children),
        )
    elif isinstance(py_node, tuple):
        log.debug("Python node is a tuple.")
        return react.createElement(react.Fragment, None, *get_array(py_node))
    elif isinstance(py_node, str):
        log.debug("Python node is a string.")
        return py_node
    elif isinstance(py_node, HTMLElement):
        log.debug("Python node is an HTMLElement.")
        log.debug(f"Children: {py_node._children}")
        return get_react_html_element(py_node)
    elif is_iterable(py_node):
        log.debug("Python node is iterable.")
        return get_array(py_node)
    elif py_node is None:
        log.debug("Python node is None.")
        return None
    else:
        log.debug("Default: Python node will be converted to a string.")
        return str(py_node)


def ReactComponent(props):
    renderer = props["renderer"]
    args = props["args"]
    kwargs = props["kwargs"]
    py_children = list(props["pyChildren"])
    result = renderer(*args, **kwargs)
    print("result:", result)
    print("is_generator:", is_generator(result))
    if is_generator(result):
        next(result)
        try:
            if len(py_children) == 1:
                result.send(py_children[0])
            else:
                result.send(py_children)
        except StopIteration as exc:
            py_node = exc.value
    else:
        py_node = result
    react_node = get_react_node(py_node)
    js.console.log("React node:", react_node)
    return react_node


def get_array(py_iterable):
    log.debug(f"py_iterable: {repr(py_iterable)}")
    ret = js.Array.new()
    for item in py_iterable:
        log.debug(f"item: {repr(item)}")
        item_react = get_react_node(item)
        log.debug(f"item_react: {repr(item_react)}")
        ret.push(item_react)
    log.debug(f"Built JavaScript Array: {repr(ret)}")
    return ret


def get_react_html_element(py_node):
    attrs = {}
    has_ref = False
    for k, v in py_node._attrs.items():
        if k == "ref":
            has_ref = True
            continue
        attrs[k] = v
    if has_ref:
        attrs["ref"] = py_node._attrs["ref"]._ref_proxy
    return react.createElement(
        py_node._tagname,
        attrs,
        # to_js(attrs),
        *get_array(py_node._children),
    )
