from collections.abc import AsyncGenerator, Callable, Generator
from numbers import Number
from pathlib import Path
from types import EllipsisType
from blu._utils.typing import Any, Mapping, Protocol, Sequence, cast
from blu._utils.client import is_client

from blu._exceptions import WrongEnvironmentError

from ._utils import py_to_html_name

# """
# JSON-serializable primitive value.
# """
type JsonPrimitive = bool | Number | str | None


# """JSON-serializable value."""
type Jsonable = JsonPrimitive | Sequence[Jsonable] | Mapping[str, Jsonable]

# """Basic item that can serialized and sent from server to client."""
type SerializableItem = JsonPrimitive | Node

# """Can be serialized and sent from server to client."""
type Serializable = (
    SerializableItem | Sequence[Serializable] | Mapping[str, Serializable]
)

type Node = '''
    CustomElement |
    ClientElement[...] |
    HTMLElement |
    Key |
    Sequence[Node] |
    str |
    int |
    float |
    bool |
    None
'''
"""
A valid child of a `ReactElement`.

.. note::

    Even though a :py:class:`tuple` is a
    :py:class:`abc.collections.Iterable`, :py:class:`tuple`\\ s are not
    valid nodes in Blu.
"""

# """Valid value for a prop of a `ReactElement`."""
type PropValue = Jsonable | Node


def is_jsonable(item: Any) -> bool:
    if item is None:
        return True
    elif isinstance(item, (bool, Number, str)):
        return True
    elif isinstance(item, Sequence):
        items = cast(Sequence[Any], item)
        return all(is_jsonable(x) for x in items)
    elif isinstance(item, Mapping):
        props = cast(Mapping[str, Any], item)
        return all(is_jsonable(v) for v in props.values())
    else:
        return False


def is_node(item: Any) -> bool:
    """
    :return: :py:data:`True` if ``item`` is a valid :type:`Node`,
        otherwise :py:data:`False`.
    """
    node_types = (bool, Number, str, HTMLElement, CustomElement)
    if item is None:
        return True
    elif isinstance(item, node_types):
        return True
    elif isinstance(item, Sequence):
        seq = cast(Sequence[Any], item)
        return all(is_node(x) for x in seq)
    else:
        return False


# """Valid props for a `ReactElement`."""
type Props = Mapping[str, PropValue]

# """Valid children of a `ReactElement`."""
type Children = list[Node]


class HTMLElement:
    """
    Server-side representation of a React html element, i.e. a React
    element whose type is a string. Created using the :mod:`blu.html`
    module.

    .. code-block:: python

        from blu import html

        html.div(id='my-id')[
            'Hello World!',
        ]

        html('div')(id='my-id')[
            'Hello World!',
        ]
    """

    _tagname: str
    """
    The tag name of the element.

    .. code-block:: python

        from blu.html import span

        span.tagname == 'span'
    """

    _attrs: Props
    """
    The element's props, minus children.

    .. code-block:: python

        from blu.html import div

        div(id='my-id')['Hello!'].props == {'id': 'my-id'}
    """

    _children: list[Node]
    """
    The element's children.

    .. code-block:: python

        from blu.html import div, span

        div[span['Hello'], 'Hi.'].children == [span['Hello'], 'Hi.']
    """

    def __init__(self, tagname: str, props: Props, children: Children):
        self._tagname = tagname
        self._attrs = props
        self._children = children

    def __call__(
        self, /, attributes: Props = {}, **kwargs: PropValue
    ) -> 'HTMLElement':
        """
        Create a copy of :data:`self` with the same :data:`children` but
        with :data:`props` set based on the given keyword arguments.

        .. code-block:: python

            from blu.html import div

            div(id='my-div')  # <div id="my-div" />

        :param attributes: A mapping of prop names to prop values. This
            is an escape hatch for cases when the prop name can't be
            represented as a keyword argument name.

        :param kwargs: The new props.

        :return: A copy of :data:`self` with the same :data:`children`
            but with :data:`props` set as follows:

            1. For any key-value pair in the :data:`attributes`
               argument, the prop named by the key will be set to the
               value.

               For example, :data:`div(attributes={'my_prop_': 45})`
               results in the React element ``<div my_prop_={45} />``

            2. For any keyword argument, the value will be set to a key
               derived from:

               - Removing the last trailing underscore (if any).
               - Replacing all other underscores with dashes.

               For example, :data:`div(my_prop_=45)` results in the
               React element ``<div my-prop={45} />``.

            3. If there is any conflict between the :data:`attributes`
               argument and the keyword arguments, the prop that has the
               conflict will be set based on the :data:`attributes`
               argument as described in (1). Any props that do not have
               conflicts will be set the same way they otherwise would,
               irrespective of the props that do have conflicts.

               For example,
               :data:`div(attributes={'props-only': 'props', 'shared': 'props'}, shared='kw', kw_only='kw')`
               results in the React element
               ``<div props-only="props" shared="props kw-only="kw" />``
        
        .. note:: Calling an :class:`HTMLElement` does not mutate the
            original :class:`HTMLElement`; it instead returns a copy
            with the given props.

            .. code-block:: python

                from blu.html import div

                div  # <div />

                div(id='my-id')  # <div id="my-id" />

                div  # Still <div />

        .. note:: When calling an :class:`HTMLElement`, the copy
            returned does not keep any of the original's non-children
            props except those explicity specified in the call:

            .. code-block:: python

                from blu.html import div

                first = div(a=1, b=2, c=3)  # <div a={1} b={2} c={3} />

                second = div(c=3, d=4, e=5)  # <div c={3} d={4} e={5} />

        .. note:: When calling an :class:`HTMLElement`, the copy's
            :attr:`children` are unchanged
            from the original's.
        
        .. note:: A prop value must either be a :type:`blu.Node` or a
            :type:`blu.Jsonable`; they will be sent from the server to
            the client and so need to be serializable.
        
        .. note:: ``children`` is not a valid prop name in Blu. To set
            React children, use the index operator (:data:`[]`).
        """
        all_props = {
            **self._rename_props(kwargs),
            **self._rename_props(attributes),
        }
        for prop_name in all_props:
            if not is_client and prop_name.startswith('on'):
                raise WrongEnvironmentError(
                    f'Could not add attribute "{prop_name}" to {self.tagname} '
                    f'element. Event-handling attributes like "{prop_name}" '
                    'can only be set in client-side rendering; this code was '
                    'run server-side.'
                )
        return HTMLElement(
            self._tagname,
            props=all_props,
            children=self._children,
        )

    def __getitem__(
        self, index: Node | EllipsisType | tuple[Node, ...]
    ) -> 'HTMLElement':
        """
        Return a copy of `self` with the same props, but with child
        nodes set to the items passed in.

        .. code-block:: python

            from blu.html import div

            div['Hello World!']  # <div>Hello World!</div>
        
        :param index: A :type:`blu.Node`, a :py:class:`tuple` of
            :type:`blu.Node`\\ s, or :py:data:`... <ellipsis>`.
        :return:
            - If :data:`index` is a :type:`blu.Node`: A copy of
              :data:`self` with :data:`children` set to :data:`[index]`.
            - If :data:`index` is a :py:class:`tuple` of
              :type:`blu.Node`\\ s: A copy of :data:`self` with
              :data:`children` set to :data:`list(index)`.
            - If :data:`index` is :py:data:`... <ellipsis>`: A copy of
              :data:`self` with :data:`children` set to :data:`[]`
        
        .. note:: Using the index operator (:data:`[]`) on an
            :data:`HTMLComponent` does not mutate the original
            :data`HTMLComponent; insteadd, it returns a copy of the
            :data:`HTMLComponent` with the given *children*.
        
        .. include:: /_includes/iterables-must-use-keys-note.rst
        """

        # For example, to generate a div with two spans in it:

        # ```
        # from reactssr import html

        # html.div[
        #     html.span,
        #     html.span,
        # ]  # renders as <div><span></span><span></span></div>
        # ```

        # You can use `...` as a placeholder for when you know there will
        # be children, but have not yet implemented that part of the view:

        # ```
        # from reactssr import html

        # html.div[
        #     ...
        # ]  # renders as <div></div>
        # ```

        # :param index: The child nodes for the new `ReactElement`.

        # :return: A copy of `self`, but with `children` set to the
        # children passed into the index operator.
        # """
        return HTMLElement(
            self._tagname,
            props=self._attrs,
            children=_index_to_children(index),
        )
    
    def _rename_props(self, props: Props) -> Props:
        return {py_to_html_name(k): v for k, v in props.items()}


class CustomElement:
    """
    Server-side representation of a React element whose type is a React
    function component. Created using :func:`blu.import_client`.

    .. code-block:: python

        from blu import import_client

        MyComponent = import_client('/path/to/module', 'MyComponent')
    """

    module: Path
    """
    The path portion of the URL of the module containing the element's
    component type.

    .. code-block:: python

        from blu import import_client

        MyComponent = import_client('/path/to/module', 'MyComponent')
        MyComponent.path == '/path/to/module'

    """

    name: str
    """
    The export name of the component.

    .. code-block:: python

        from blu import import_client

        NamedImport = import_client('/path/to/module', 'MyComponent')
        NamedImport.name == 'MyComponent'

        DefaultImport = import_client('/path/to/module')
        DefaultImport.name == 'default'
    """

    props: Props
    """
    The React element's props, other than `children`.

    .. code-block:: python

        from blu import import_client

        MyComponent = import_client('/MyComponent')
        
        MyComponent(my_prop=5)['Hello World!'].props == {'my_prop': 5}
    """

    children: list[Node]
    """
    The React element's `children` prop.

    .. code-block:: python

        from blu import import_client
        from blu.html import div, span

        MyComponent = import_client('/MyComponent')
        with_children = MyComponent[span['Hello'], div, 'Hi.']
        with_children.children == [span['Hello'], div, 'Hi.']
    """

    def __init__(
        self,
        path: Path | str,
        name: str,
        props: Props,
        children: Children,
    ):
        self.path = Path(path)
        self.name = name
        self.props = props
        self.children = children
    
    def __call__(self, **kwargs: PropValue) -> 'CustomElement':
        """
        Create a copy of :data:`self` with the props specified by
        ``kwargs``.

        .. code-block:: python
        
            from blu import import_client

            MyComponent = import_client('/MyComponent')

            MyComponent(my_prop='value')

        :param kwargs: The new props.
        :return: A copy of :data:`self`, with :data:`props` replaced by
            ``kwargs``.

        .. note:: Calling a :class:`CustomElement` does not change the
            original :class:`CustomElement`; it just returns a copy with
            the given props.

            .. code-block:: python

                from blu import import_client

                MyComponent = import_client('/MyComponent')

                MyComponent  # <MyComponent />

                # <MyComponent my_prop={'value'} />
                MyComponent(my_prop='value')

                MyComponent  # Still <MyComponent />
        
        .. note:: When calling a :class:`CustomElement`, the copy
            returned does not keep any of the original's non-children
            props except those explicitly specified in the call:

            .. code-block:: python

                from blu import import_client

                MyComponent = import_client('/MyComponent')

                # <MyComponent a={1} b={2} c={3} />
                first = MyComponent(a=1, b=2, c=3)

                # <MyComponent c={3} d={4} e={5} />
                second = first(c=3, d=4, e=5)
        
        .. note:: When calling a :class:`CustomElement`, the copy's
            :data:`children` are unchanged from the original's:

            .. code-block:: python

                from blu import import_client

                MyComponent = import_client('/MyComponent')

                # <MyComponent a={1}>Hello!</MyComponent>
                first = MyComponent(a=1)['Hello!']

                # <MyComponent b={2}>Hello!</MyComponent>
                second = first(b=2)
        
        .. note:: ``children`` is not a valid prop name in Blu. To set
            React children, use the index operator (:data:`[]`).
        """
        return CustomElement(
            path=self.path,
            name=self.name,
            props=kwargs,
            children=self.children,
        )

    def __getitem__(
        self, index: Node | EllipsisType | tuple[Node, ...]
    ) -> 'CustomElement':
        """
        Create a copy of :data:`self` with the :data:`children`
        specified by :data:`index`.

        .. code-block:: python

            from blu import import_client
            from blu.html import span

            MyComponent = import_client('/MyComponent')

            MyComponent[
              span['Hello World!'],
            ]

        
        :param index: A :type:`blu.Node`, a :py:class:`tuple` of
            :type:`blu.Node`\\ s, or :py:data:`... <ellipsis>`.
        :return:
            - If ``index`` is a :type:`blu.Node`: A copy of ``self``
              with :attr:`children <blu.CustomElement.children>` set to
              ``[index]``.
            - If ``index`` is a :py:class:`tuple` of
              :type:`blu.Node`\\ s: A copy of ``self`` with
              :attr:`children <blu.CustomElement.children>` set to
              ``list(index)``.
            - If ``index`` is :py:data:`... <ellipsis>`: A copy of
              ``self`` with
              :attr:`children <blu.CustomElement.children>` set to
              ``[]``.

        .. note::
        
            Using the index operator (:data:`[]`) on a
            :class:`CustomComponent` does not mutate the original
            :class:`CustomComponent`; instead, it returns a copy of the
            :class:`CustomComponent` with different children:

            .. code-block:: python

                from blu import import_client

                MyComponent = import_client('/MyComponent')

                MyComponent  # <MyComponent />

                # <MyComponent>Hello!</MyComponent>
                MyComponent['Hello!']

                MyComponent  # Still <MyComponent />
        """
        return CustomElement(
            path=self.path,
            name=self.name,
            props=self.props,
            children=_index_to_children(index),
        )


def _index_to_children(
    index: Node | EllipsisType | tuple[Node, ...]
) -> Children:
    if index == ...:
        children = []
    elif isinstance(index, tuple):
        children = list(cast(tuple[Node], index))
    else:
        children = [index]
    for child in children:
        if child is not None and not isinstance(
            child,
            (HTMLElement, CustomElement, ClientElement, Sequence, str, Number, bool),
        ):
            raise TypeError(
                'HTMLElement\'s children must be valid nodes, i.e. they '
                'must be one of the following types: '
                '`blu.react.HTMLElement`, '
                '`blu.react.CustomElement`, `typing.Sequence`, '
                f'`str`, `int`, `float`, `None`. Got {child}'
            )
    return children


class Key:
    key: Any
    children: list[Node]

    def __init__(self, key: Any, children: list[Node] = []):
        self.key = key
        self.children = children

    def __getitem__(self, children: Node | EllipsisType) -> 'Key':
        actual_children: list[Node]
        if isinstance(children, EllipsisType):
            actual_children = []
        elif isinstance(children, tuple):
            actual_children = list(children)
        else:
            actual_children = [children]
        return Key(self.key, actual_children)


type ElementRenderer[**P] = Callable[
    P,
    Node | Generator[None, Node, Node] | AsyncGenerator[None | Node, Node]
]


class Element[**P](Protocol):

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> 'Element[P]':
        ...
    
    def __getitem__(self, *children: 'Node') -> 'Element[P]':
        ...


class ClientElement:
    """
    A custom element to be rendered client-side. Created using the
    :func:`blu.client` decorator.

    .. code-block:: python

        from blu import client
        from blu.html import b, span

        __client__ = True

        
        @client
        def ColorfulText(color, bold):
            colorful_span = span(style={'color': color})[
                (yield)
            ]
            if bold:
                return b[colorful_span]
            else:
                return colorful_span

                
        ColoredText('red', bold=True)[
            'Danger! The world said hello back.',
        ]

    .. code-block:: html

        <b>
            <span style="color: red">
                Danger! The world said hello back.
            </span>
        </b>
    """
    
    _args: tuple[Any, ...]
    _kwargs: dict[str, Any]
    _children: list['Node']
    _renderer: ElementRenderer

    def __init__(
        self,
        renderer: ElementRenderer,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        children: Sequence[Node],
    ):
        self._renderer = renderer
        self._args = args
        self._kwargs = kwargs
        self._children = list(children)

    def __call__(self, *args: Any, key: Any, **kwargs: Any) -> 'ClientElement':
        """
        Create a copy of self with the given call args.

        .. code-block:: python

            from blu import client
            from blu.html import div

            __client__ = True


            @client
            def Greeting(name = 'World'):
                return div[f'Hello, {name}!']

            
            div[
                Greeting('Arnold'),
                Greeting(name='Hailey'),
                Greeting,
            ]

        .. code-block:: html

            <div>
                <div>Hello, Arnold!</div>
                <div>Hello, Hailey!</div>
                <div>Hello, World!</div>
            </div>

        
        
        :param *args: The positional arguments to pass into the
            element's render function when it is rendered.
        :param key: A key that uniquely identifies this element.
            Usually, you won't need this, but it's required for any
            :py:class:`ClientElement <blu.ClientElement>` that is
            rendered as an item in an
            :py:class:`Iterable <collections.abc.Iterable>` (unless that
            :py:class:`Iterable <collections.abc.Iterable>` is a
            :py:class:str or a :py:class:tuple):

            .. code:: python

                from blu.html import div

                PEOPLE = [
                    {'id': 1, 'name': 'Amy'},
                    {'id': 2, 'name': 'Bill'},
                    {'id': 3, 'name': 'Carrie' },
                ]

                @client
                def 

                div[

                ]

        :param **kwargs: The keyword arguments to pass into the
            element's render function when it is rendered.

        :return: A copy of ``self`` with call arguments set to ``*args``
            and ``**kwargs``.
        
        .. include:: /_includes/client-element-call-notes.rst
        """
        return ClientElement(
            self._renderer,
            args,
            kwargs,
            self._children,
        )

    def __getitem__(self, *children: 'Node') -> 'ClientElement':
        """
        .. include:: /_includes/client-element-children.rst

        :param children: Any valid :type:`blu.Node`\s.
        :return: A copy of the ``self``, with the children replaced by
            ``children``.
        """
        return ClientElement(
            self._renderer,
            self._args,
            self._kwargs,
            _index_to_children(children),
        )
