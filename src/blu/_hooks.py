from collections.abc import AsyncGenerator, Callable, Coroutine, Generator
from typing import Any
import typing
from blu._utils import is_client

if is_client or typing.TYPE_CHECKING:
    from pyscript.ffi import create_proxy, to_js
    from pyodide.ffi import JsDoubleProxy
    from pyscript.js_modules._blu_js_utils import useEffect, useRefObj, useState


def use_effect(
    callback: Callable[
        [],
        None
        | Generator[None]
        | Coroutine[None, None, None]
        | AsyncGenerator[None, None],
    ],
):
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

    :param callback: A plain function, an ``async def`` function, a
        generator function with a single ``yield``, or an ``async def``
        generator function with a single ``yield``.

    If ``callback`` is a (sync) generator function, it will be run right
    up until the ``yield`` statement immediately after the element is
    initially rendered to the DOM. The rest of the function will be run
    immediately before the element is removed from the DOM.

    If ``callback`` is an async generator function, the same pattern
    applies: code up to the first ``yield`` runs after render; the
    remainder runs on teardown.

    If ``callback`` is a plain function, it is called synchronously
    after render. If it is an ``async def`` function (not a generator),
    the coroutine is scheduled and runs on the asyncio event loop; it
    has no separate teardown hook beyond hook cleanup.
    """
    useEffect(callback)


def use_state[T](init: T = None) -> tuple[T, Callable[[T], None]]:
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
    return tuple(useState(init))


class Ref[T]:
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
    _ref_proxy: Any

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
        if empty_slice.start or empty_slice.stop or empty_slice.step:
            raise
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
        if empty_slice.start or empty_slice.stop or empty_slice.step:
            raise
        self._value = new_value


class RefOld[T]:
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

    _js_ref: Any

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
        print("EMPTY SLICE:", empty_slice)
        if empty_slice.start or empty_slice.stop or empty_slice.step:
            raise
        current = self._js_ref.current
        if isinstance(current, JsDoubleProxy):
            return current.unwrap()
        else:
            return current

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
        if empty_slice.start or empty_slice.stop or empty_slice.step:
            raise
        try:
            current = self._js_ref.current
        except AttributeError:
            pass
        else:
            current.destroy()
        self._js_ref.current = create_proxy(new_value)

    def _cleanup(self):
        try:
            current = self._js_ref.current
        except AttributeError:
            pass
        else:
            if isinstance(current, JsDoubleProxy):
                current.destroy()


def use_ref[T](init: T = None) -> Ref[T]:
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
    ref: Ref[T] = Ref()
    ref[:] = init
    return useRefObj(ref)
