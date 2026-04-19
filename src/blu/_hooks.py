from collections.abc import AsyncGenerator, Callable, Coroutine, Generator
from typing import Any
import typing

from blu._utils import is_client

if is_client or typing.TYPE_CHECKING:
    from pyscript.js_modules._blu_js_utils import useEffect, useRefObj, useState

# Integers for JS `useEffect` (avoid classifying return values in JS, where
# coroutines can be finalized before `isinstance` runs).
_use_effect_ag_phase: dict[int, str] = {}

# String tags for JS (reliable compare; PyProxy int coercion was flaky).
_USE_EFFECT_TAG_ASYNC_GENERATOR = "async_generator"
_USE_EFFECT_TAG_COROUTINE = "coroutine"
_USE_EFFECT_TAG_GENERATOR = "generator"
_USE_EFFECT_TAG_PLAIN = "plain"


def _unwrap_js_proxy(obj: Any) -> Any:
    """Resolve Pyodide ``JsProxy`` so ``id`` matches the underlying Python object."""
    if not is_client:
        return obj
    try:
        from pyodide.ffi import JsProxy
    except ImportError:
        return obj
    while isinstance(obj, JsProxy):
        obj = obj.unwrap()
    return obj


def _use_effect_invoke(callback: Callable[[], Any]) -> tuple[str, Any]:
    """Call ``callback()`` and classify the return value for ``util.js`` ``useEffect``."""
    from collections.abc import AsyncGenerator as AsyncGenABC
    from collections.abc import Coroutine as CoroutineABC
    from collections.abc import Generator as GenABC

    result = callback()
    if isinstance(result, AsyncGenABC):
        _use_effect_start_async_gen(result)
        return (_USE_EFFECT_TAG_ASYNC_GENERATOR, result)
    if isinstance(result, CoroutineABC):
        _use_effect_start_coro(result)
        return (_USE_EFFECT_TAG_COROUTINE, result)
    if isinstance(result, GenABC):
        return (_USE_EFFECT_TAG_GENERATOR, result)
    return (_USE_EFFECT_TAG_PLAIN, result)


def _use_effect_start_async_gen(agen: AsyncGenerator[Any, None]) -> None:
    """Schedule running an async generator up to its first ``yield``."""
    import asyncio

    agen = _unwrap_js_proxy(agen)
    aid = id(agen)
    _use_effect_ag_phase[aid] = "pending"

    async def setup() -> None:
        await anext(agen)
        _use_effect_ag_phase[aid] = "after_yield"

    asyncio.create_task(setup())


def _use_effect_cleanup_async_gen(
    agen: AsyncGenerator[Any, None],
    on_done: Callable[[], None] | None = None,
) -> None:
    """Schedule teardown or ``aclose`` for an effect async generator.

    ``on_done`` runs after async work finishes (e.g. to release JS proxies). The
    client must not destroy ``agen`` until then, or the cleanup task may see a
    dead generator.
    """
    import asyncio

    agen = _unwrap_js_proxy(agen)

    async def work() -> None:
        try:
            aid = id(agen)
            phase = _use_effect_ag_phase.pop(aid, "pending")
            if phase == "after_yield":
                try:
                    await anext(agen)
                except StopAsyncIteration:
                    pass
            else:
                try:
                    await agen.aclose()
                except Exception:
                    pass
        finally:
            if on_done is not None:
                on_done()

    asyncio.create_task(work())


def _use_effect_start_coro(coro: Coroutine[Any, Any, Any]) -> None:
    import asyncio

    asyncio.create_task(coro)


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
