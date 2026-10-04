from logging import getLogger

from blu._utils import is_client
from blu._micropython.abc import Callable, Generator
from blu._micropython import typing
from blu._micropython.typing import Generic, TypeVar
from blu._micropython.utils import is_generator

if is_client or typing.TYPE_CHECKING:
    import _react as react
    import js

log = getLogger("blu")

# if is_client or typing.TYPE_CHECKING:
#     from pyscript.js_modules._blu_js_utils import useEffect, useRefObj, useState

T = TypeVar("T")


def use_effect(callback: Callable[[], None | Generator[None]]):
    """
    .. include:: /_includes/hook-note.rst

    Perform set-up actions immediately after a :class:`ClientElement
    <blu.ClientElement>` is rendered to the DOM and/or tear-down actions
    immediately before it is removed from the DOM.

    .. code-block:: python

        from blu import client, use_effect
        from blu.html import div

        __client__ = True


        @client
        def MyClientElement():

            @use_effect
            def setup_and_teardown():
                do_some_setup()
                yield
                do_some_teardown()

            return div['Hello!']

    :param callback: A non-generator function or a generator function
        with a single ``yield`` statement.

    If ``callback`` is a generator function or async generator function,
    it will be run right up until the ``yield`` statement immediately
    after the element is initially rendered to the DOM. The rest of the
    function will be run immediately before the element is removed from
    the DOM.

    Otherwise, ``callback`` will be called immediately after the element
    is initially rendered to the DOM.
    """

    def react_callback():
        log.debug("calling use_effect_callback")
        result = callback()
        log.debug("called use_effect_callback")
        if is_generator(result):
            log.debug("use_effect callback result is a generator.")
            next(result)

            def ret():
                try:
                    next(result)
                except StopIteration:
                    pass

            return ret
        else:
            return js.undefined

    react.useEffect(react_callback)


def use_state(init: T = None) -> tuple[T, Callable[[T], None]]:
    """
    .. include:: /_includes/hook-note.rst

    Handle state management for an element.

    .. code-block:: python

        from blu import client
        from blu.html import button

        __client__ = True


        @client
        def MyElement():
            click_count, set_click_count = use_state(0)

            def handle_click(e):
                set_click_count(click_count + 1)

            return (
                button(onClick=handle_click)[
                    f'You\\'ve clicked {click_count} times',
                ]
            )

    :param init: An initial value for the state being managed.
    :return: A tuple containing two items: The current value for the
        state being managed, and a function that takes any value and
        causes the element whose render function ``use_state`` was
        called in to re-render. On a re-render triggered by this setter,
        the first item in the tuple will be whatever was passed into the
        setter when the re-render was triggered. On a re-render not
        triggered by this state's setter, the first item in the tuple
        will be whatever it was in the previous render. On the initial
        render, the first item in the tuple will be ``init``.

    """
    return tuple(react.useState(init))


class Ref(Generic[T]):
    """
    The object returned by :func:`blu.use_ref`.

    .. code-block:: python

        from blu import client
        from blu.tml import button

        __client__ = True


        @client
        def TwoButtons():
            # assigns variable ref to an instance of Ref.
            ref = use_ref()
    """

    _value: T

    def __getitem__(self, empty_slice: slice) -> T:
        """
        Get the value currently stored in the :class:`Ref <blu.Ref>`.

        .. code-block:: python

            from blu import client
            from blu.html import button

            __client__ = True


            @client
            def TwoButtons():
                ref = use_ref('Hello')
                ref[:]  # 'Hello'

        :param empty_slice: Must be an empty slice, i.e. you must put a
            single colon between the square brackets, without any
            numbers.
        :return: The value currently stored in ``self``.
        """
        return self._value

    def __setitem__(self, empty_slice: slice, new_value: T):
        """
        Set the :class:`Ref <blu.Ref>` to point to a different value.

        .. code-block:: python

            from blu import client
            from blu.tml import button

            __client__ = True


            @client
            def TwoButtons():
                ref = use_ref('Hello')
                ref[:] = 'Goodbye'
                ref[:]  # 'Goodbye'

        :param empty_slice: Must be an empty slice, i.e. you must put a
            single colon between the square brackets, without any
            numbers.
        :param new_value: The new value that should be stored in
            ``self``.

        Once this method has been called, the :class:`Ref <blu.Ref>`\\'s
        stored value will be set to ``new_value``.
        """
        self._value = new_value


def use_ref(init: T = None) -> Ref[T]:
    """
    .. include:: /_includes/hook-note.rst

    Store a value that doesn't change between renders unless explicitly
    set to a new value.

    .. code-block:: python

        from blu import client, is_client, use_ref
        from blu.html import button

        if is_client:
            from js import alert

        __client__ = True


        @client
        def MyElement():
            click_count_ref = use_ref(0)

            def handle_click(e):
                click_count_ref[:] = click_count_ref[:] + 1
                count = click_count_ref[:]
                alert(f'You\\'ve clicked the button {count} times.')

            return button['Click me!']

    :param init: Any value.
    :return: A :class:`Ref <blu.Ref>`. This will be the same
        :class:`Ref <blu.Ref>` object on every render of the same
        element. On the initial render, the value stored in the
        :class:`Ref <blu.Ref>` will be ``init``, but you can set this to
        a new value at any time (see :class:`blu.Ref` for how to set a
        :class:`Ref <blu.Ref>`\\'s value).

    .. note::

        Setting a :class:`Ref <blu.Ref>`\\'s value does not trigger a
        re-render.
    """
    ref = Ref()
    ref[:] = init
    ref_ref = react.useRef(ref)
    return ref_ref.current
