from collections.abc import Mapping, Sequence
from numbers import Number
from typing import Any, Literal, NotRequired, TypedDict, cast

from blu._react.types import HTMLElement, Key, Node, PropValue, CustomElement


type Jsonable = (
    None  |
    bool  |
    int   |
    float |
    str |
    Sequence['Jsonable'] |
    'JsonObject'
)
"""JSON-serializable object."""

type JsonObject = Mapping[str, Jsonable]
"""
JSON-serializable :py:class:`collections.abc.Mapping` representing a
JSON object.
"""


class ReactDict(TypedDict):
    type: Literal['rendered_element', 'native_element', 'fragment', 'object']


class ReactJsObject(ReactDict):
    type: Literal['object']  # type: ignore
    data: JsonObject


class ReactElementDict(ReactDict):
    type: Literal[  # type: ignore
        'rendered_element', 'native_element', 'fragment'
    ]
    props: dict[str, Jsonable]
    children: list['ReactNodeJson']


class RenderedElementDict(ReactElementDict):
    type: Literal['rendered_element']  # type: ignore
    module: str
    name: str


class NativeElementDict(ReactElementDict):
    type: Literal['native_element']  # type: ignore
    tagname: str


class FragmentDict(ReactElementDict):
    type: Literal['fragment']  # type: ignore
    key: NotRequired[Any]


type ReactNodeJson = (
    None | bool | Number | str | ReactDict | list[ReactNodeJson]
)


def get_react_data(node: Node | PropValue) -> ReactNodeJson:
    if node is None or isinstance(node, (bool, Number, str)):
        return node
    if isinstance(node, Sequence):
        return [get_react_data(x) for x in node]
    if isinstance(node, Key):
        return cast(FragmentDict, {  # type: ignore
            'type': 'fragment',
            'key': node.key,
            'children': node.children,
        })
    if isinstance(node, HTMLElement):
        return cast(ReactElementDict, {  # type: ignore
            'type': 'native_element',
            'tagname': node.tagname,
            'props': {
                k: get_react_data(v)
                for k, v in node.props.items()
            },
            'children': [get_react_data(x) for x in node.children],
        })
    if isinstance(node, CustomElement):
        return cast(RenderedElementDict, {  # type: ignore
            'type': 'rendered_element',
            'module': str(node.path),
            'name': node.name,
            'props': {
                k: get_react_data(v) for k, v in node.props.items()
            },
            'children': [get_react_data(x) for x in node.children],
        })
    if isinstance(node, Mapping):
        return cast(ReactJsObject, {  # type: ignore
            'type': 'object',
            'data': node,
        })
