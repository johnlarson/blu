import base64

# from importlib import import_module
import logging

# import pickle
from blu.mPickle import mpickle as pickle

from js import document  # type: ignore
from pyscript.ffi import create_proxy, to_js  # type: ignore
import _react as react
import _react_dom as react_dom

from blu._nodes import ClientRenderer, ClientElement, HTMLElement, Node, Key
from blu._micropython.typing import Any, cast
from blu._micropython.utils import import_module, is_generator, is_iterable

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
    # _blu_js_utils.init(import_module)  # type: ignore
    b64_str: str = cast(str, document.querySelector('script[type="react-data"]').textContent)  # type: ignore
    b64_bytes = b64_str.encode("ascii")
    pickled = base64.b64decode(b64_bytes)
    unpickled = pickle.loads(pickled)
    # _blu_js_utils.renderRoot(unpickled)  # type: ignore
    render_root(unpickled)


def render_root(py_root):
    js_root = get_react_node(py_root)
    render_target = document if js_root.type == "html" else document.body
    react_dom.createRoot(render_target).render(js_root)


def get_react_node(py_node):
    if isinstance(py_node, ClientElement):
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
        return react.createElement(
            react.Fragment,
            {
                "key": py_node._key,
            },
            *get_array(py_node._children),
        )
    elif isinstance(py_node, tuple):
        return react.createElement(react.Fragment, null, *get_array(py_node))
    elif isinstance(py_node, str):
        return py_node
    elif is_iterable(py_node):
        return get_array(py_node)
    elif isinstance(py_node, HTMLElement):
        return get_react_html_element(py_node)
    elif py_node is None:
        return None
    else:
        return str(py_node)


def ReactComponent(props):
    renderer = props["renderer"]
    args = props["args"]
    kwargs = props["kwargs"]
    py_children = list(props["pyChildren"])
    result = renderer(*args, **kwargs)
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
    return get_react_node(py_node)


def get_array(py_iterable):
    ret = js.Array.new()
    for item in py_iterable:
        ret.push(get_react_node(item))
    return ret


def get_react_html_element(py_node):
    attrs = {}
    has_ref = False
    for k, v in py_node._attrs.items():
        if k == ref:
            has_ref = True
            continue
        attrs[k] = v
    if has_ref:
        attrs["ref"] = py_node._attrs["ref"]._ref_proxy
    return react.createElement(
        py_node._tagname,
        to_js(attrs),
        *py_node._children,
    )


# def get_node(data: Any):
#     if isinstance(data, ClientElement):
#         return react.createElement(
#             PythonElement,
#             to_js(
#                 {
#                     "renderer": create_proxy(data._renderer),
#                     "args": data._args,
#                     "kwargs": data._kwargs,
#                     "py_children": data._children,
#                 }
#             ),
#         )
#     elif isinstance(data, Key):
#         props = {"key": data["key"]}
#         return react.createElement(
#             react.Fragment,
#             to_js({"key": data._key}),
#             *get_array(data._children),
#         )
#     elif isinstance(data, tuple):
#         return react.createElement(
#             react.Fragment,
#             to_js({}),
#             *get_array(data),
#         )
#     elif isinstance(data, str):
#         return data
#     elif is_iterable(data):
#         return get_array(data)
#     elif isinstance(data, HTMLElement):
#         props = {k: v for k, v in data._attrs.items() if k != "ref"}
#         if "ref" in data._attrs.keys():
#             props["ref"] = data._attrs["ref"]._js_ref
#         return react.createElement(
#             data._tagname,
#             to_js(props),
#             *get_array(data._children),
#         )
#     elif data is None:
#         return None
#     else:
#         return str(data)


# def get_obj(obj: dict[str, Any]):
#     return {k: get_node(v) for k, v in obj.items()}


# def get_dict(my_dict: dict):
#     return {k: get_node(v) for k, v in my_dict.items()}


# def get_array(array: Any):
#     return to_js([get_node(x) for x in array])


# class PythonElementProps(TypedDict):
#     renderer: ClientRenderer
#     args: tuple[Jsonable, ...]
#     kwargs: dict[str, Jsonable]
#     py_children: list[Node]


# @create_proxy
# def PythonElement(props: PythonElementProps, extra: Any = None):
#     result = props.renderer(*props.args, **props.kwargs.as_object_map())
#     if is_generator(result):
#         next(result)
#         try:
#             result.send(props.py_children)
#         except StopIteration as e:
#             return get_node(e.value)
#     elif is_async_generator(result):
#         raise TypeError(
#             "ClientElements cannot be created from async rendering functions."
#         )
#     else:
#         return get_node(result)


def py_to_js_node(py_node: Node):
    if isinstance(py_node, ClientElement):
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
    return ClientElement(
        get_renderer(data),
        get_array(data["args"]),
        get_obj(data["kwargs"]),
        get_node(data["children"]),
    )


def get_renderer(data: Any) -> ClientRenderer:
    module = import_module(data["module"])
    return getattr(module, data["name"])
