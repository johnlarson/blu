from collections.abc import (
    AsyncGenerator, Callable, Generator, Iterable
)
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
    ClientElement |
    HTMLElement |
    Key |
    Iterable[Node] |
    str |
    int |
    float |
    bool |
    None
'''

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
    A `React DOM component instance
    <https://react.dev/reference/react-dom/components>`_. Created using
    the :mod:`blu.html` module.

    .. code-block:: python

        from blu.html import div

        div(id='my-id')[
            'Hello World!',
        ]
    
    .. code-block:: html

        <div id="my-id">Hello World!</div>
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
        self, /, props: Props = {}, **kwargs: PropValue
    ) -> 'HTMLElement':
        """
        Create a copy of ``self`` with React props set based on the
        given keyword arguments.

        .. code-block:: python

            from blu.html import div

            div(id='my-div')
        
        .. code-block:: html

            <div id="my-div"></div>

        :param props: A mapping of prop names to prop values. This is an
            escape hatch for cases when the prop name can't be
            represented as a keyword argument name. Note that this is a
            keyword-only argument.

        :param kwargs: The new props, where the argument name is the
            prop's key and the argument value is the prop's value. This
            is the usual way to specify props.

        :return: A copy of :data:`self` with the same :data:`children`
            but with :data:`props` set as follows:

            1. For any key-value pair in the :data:`props` argument, the
               prop named by the key will be set to the value.

               For example, :data:`div(props={'my_prop_': 45})`
               results in the React element ``<div my_prop_={45} />``

            2. For any keyword argument, the value will be set to a key
               derived from:

               - Removing the last trailing underscore (if any).
               - Replacing all other underscores with dashes.

               For example, :data:`div(my_prop_=45)` results in the
               React element ``<div my-prop={45} />``.

            3. If there is any conflict between the :data:`attributes`
               argument and the keyword arguments, the prop that has the
               conflict will be set based on the :data:`props`
               argument as described in (1). Any props that do not have
               conflicts will be set the same way they otherwise would,
               irrespective of the props that do have conflicts.

               For example,
               :data:`div(props={'props-only': 'props', 'shared': 'props'}, shared='kw', kw_only='kw')`
               results in the React element
               ``<div props-only="props" shared="props" kw-only="kw" />``
        
        .. note:: ``children`` is not a valid prop name in Blu. To set
            React children, use the index operator (:data:`[]`).
        """
        all_props = {
            **self._rename_props(kwargs),
            **self._rename_props(props),
        }
        for prop_name in all_props:
            if not is_client and prop_name.startswith('on'):
                raise WrongEnvironmentError(
                    f'Could not add attribute "{prop_name}" to {self._tagname} '
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
        self, children: Node | tuple[Node, ...]
    ) -> 'HTMLElement':
        """
        Create a copy of ``self`` whose child nodes are set to the items
        passed in.

        .. code-block:: python

            from blu.html import div

            div['Hello World!']

        .. code-block:: html

            <div>Hello World!</div>
        
        :param children: A :type:`blu.Node` or a :py:class:`tuple` of
            :type:`blu.Node`\\ s.
        :return:
            - If ``children`` is a :type:`blu.Node`: A copy of
              :data:`self` whose children are set to ``[children]``.
            - If ``children`` is a :py:class:`tuple` of
              :type:`blu.Node`\\ s: A copy of :data:`self` whose
              children are set to ``list(children)``.
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
            children=_index_to_children(children),
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
        self,
        children: Node | tuple[Node, ...],
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
    """
    A keyed fragment of React nodes.

    .. code-block:: python

        from blu import Key
        from blu.html import b

        Key('my-id')[
            'Hello, ',
            b['World'],
            '!',
        ]

    .. code-block:: html

        Hello, <b>World</b>!

    :param key: A key to be used by React to uniquely identify the
        fragment.
    :return: An empty fragment identified by ``key``.

    In most cases, you won't need to use :class:`blu.Key`, but it is
    required when rendering an item in an
    :py:class:`Iterable <collections.abc.Iterable>` (unless that
    :py:class:`Iterable <collections.abc.Iterable>` is a :py:class:`str`
    or :py:class:`tuple`):

    .. code-block:: python

        from blu import Key
        from blu.html import b

        PEOPLE = [
            {'id': 1, name: 'Andy'},
            {'id': 2, name: 'Brittany'},
            {'id': 3, name: 'Calvin'},
        ]

        Key(person['id'])[
            'Hello, ',
            b[person['name']],
            '!',
        ]
        for person in PEOPLE

    .. code-block:: html

        Hello, <b>Andy</b>!
        Hello, <b>Brittany</b>!
        Hello, <b>Calvin</b>!
    """

    _key: Any
    _children: list[Node]

    def __init__(self, key: Any):
        self._key = key
        self._children = []

    def __getitem__(self, children: Node | tuple[Node]) -> 'Key':
        """
        Create a copy of ``self`` with the given children.

        .. code-block:: python

            from blu import Key
            from blu.html import b

            Key('my-id')[
                'Hello, ',
                b['World'],
                '!',
            ]

        .. code-block:: html

            Hello, <b>World</b>!

        :param children: A :type:`blu.Node` or :py:class:`tuple` of
            :type:`blu.Node`\\s.
        :return: If ``children`` is a :py:class:`tuple`, a frament whose
            children are ``list(children)``. Otherwise, a fragment whose
            children are ``[children]``.
        """
        copy = Key(self._key)
        if isinstance(children, tuple):
            copy._children = list(children)
        else:
            copy._children = [children]
        return copy


type ClientRenderer = Callable[..., Node | Generator[None, Node, Node]]


class Element[**P](Protocol):

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> 'Element[P]':
        ...
    
    def __getitem__(self, *children: 'Node') -> 'Element[P]':
        ...


UNSET = object()


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
    _renderer: ClientRenderer

    def __init__(
        self,
        renderer: ClientRenderer,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        children: Sequence[Node],
    ):
        self._renderer = renderer
        self._args = args
        self._kwargs = kwargs
        self._children = list(children)

    def __call__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> 'ClientElement':
        """
        Create a copy of ``self`` that will be rendered with the given
        arguments.

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

                <div>Hello, Arnold!</div>
                <div>Hello, Hailey!</div>
                <div>Hello, World!</div>
        
        :param *args: The positional arguments to pass into the
            element's render function when it is rendered.
        :param **kwargs: The keyword arguments to pass into the
            element's render function when it is rendered, as well as an
            optional keyword argument ``key``, which will be used by
            React to uniquely identify the element when it is rendered.
            Usually, you won't need to pass in a ``key``, but it's
            required for any :py:class:`ClientElement <blu.ClientElement>` that is
            rendered as an item in an
            :py:class:`Iterable <collections.abc.Iterable>` (unless that
            :py:class:`Iterable <collections.abc.Iterable>` is a
            :py:class:`str` or a :py:class:`tuple`).

        :return: A copy of ``self`` that will be rendered by calling its
            render function with ``*args`` and ``**kwargs``, with the
            exception that the keyword argument ``key`` will not be
            passed on to the render function and will instead be used by
            React to identify the new element.

        Below is an example of using the ``key`` argument:

        .. code-block:: python

            from blu import client
            from blu.html import div

            PEOPLE = [
                {'id': 0, 'name': 'Allison'},
                {'id': 1, 'name': 'Bill'},
                {'id': 2, 'name': 'Carrie'},
            ]


            @client
            def Greeting(name):
                return div[f'Hello, {name}!']

            
            [Greeting(x['name'], key=x['id']) for x in PEOPLE]

        .. code-block:: html

            <div>Hello, Allison!</div>
            <div>Hello, Bill!</div>
            <div>Hello, Carrie!</div>
        """
        return ClientElement(
            self._renderer,
            args,
            kwargs,
            self._children,
        )

    def __getitem__(
        self,
        children: Node | tuple[Node, ...],
    ) -> 'ClientElement':
        """
        Create a copy of ``self`` that will render with the given
        children displayed where the render function uses the ``yield``
        keyword.

        .. code-block:: python

            from blu import client
            from blu.html import span


            @client
            def RedText(text):
                return span(style={'color': 'red'})[(yield)]


            RedText['Danger! This text is red.']

        .. code-block:: html

            <span style="color: red">Danger! This text is red.</span>

        :param children: Any valid :type:`blu.Node` or a
            :py:class:`tuple` of :type:`blu.Node`\s.
        :return: A copy of ``self`` that will render with ``children``
            displayed where the element's render function uses the
            ``yield`` keyword.
        """
        return ClientElement(
            self._renderer,
            self._args,
            self._kwargs,
            _index_to_children(children),
        )
