from collections.abc import AsyncGenerator, Callable, Generator
from typing import Any
import typing
from blu._utils import is_client

if is_client or typing.TYPE_CHECKING:
    from pyscript.ffi import create_proxy
    from pyscript.js_modules._blu_react import useEffect, useRef, useState


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

    If ``callback`` is generator function, it will be run right up until
    the ``yield`` statement immediately after the element is initially
    rendered to the DOM. The rest of the function will be run
    immediately before the element is removed from the DOM.

    If ``callback`` is not a generator function, ``callback`` will be
    called immediately after the element is initially rendered to the
    DOM.
    """
    manager = EffectManager(callback)
    useEffect(manager.js_callback)


class HookManager:
    proxy: Any
    watch_list: Any

    def __init__(self):
        self.proxy = create_proxy(self)
        self.self_effect = create_proxy(self.self_effect)
        self.self_cleanup = create_proxy(self.self_cleanup)
        self.watch_list = create_proxy([])

    def self_effect(self):
        return self.self_cleanup
    
    def self_cleanup(self):
        self.self_effect.destroy()
        self.watch_list.destroy()
        self.self_cleanup.destroy()
        self.proxy.destroy()


def use_setup(manager: HookManager, long_lasting: bool = False):
    proxy = create_proxy(manager)
    if long_lasting:
        useEffect(proxy.self_effect, proxy.watch_list)
    else:
        useEffect(proxy.self_effect)
    return proxy


class EffectManager(HookManager):
    callback: Callable[[], None | Generator[None] | None] = lambda: None
    generator: Generator[None] | None = None

    def __init__(self, callback: Callable[[], None | Generator[None] | None]):
        super().__init__()
        self.callback = create_proxy(callback)
        self.js_callback = create_proxy(self.js_callback)

    def js_callback(self):
        result = self.callback()
        if isinstance(result, Generator):
            next(result)
        self.generator = result
        return self.js_cleanup
    
    def js_cleanup(self):
        if self.generator is not None:
            try:
                next(self.generator)
            except StopIteration:
                pass

    def self_cleanup(self):
        self.callback.destroy()
        self.generator.destroy()
        self.js_callback.destroy()
        super().self_cleanup()


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
    init_proxy = create_proxy(init)
    value_proxy, js_setter = useState(init_proxy)
    manager = use_setup(StateManager(init_proxy, value_proxy, js_setter))
    return manager.value_proxy.unwrap(), manager.setter


class StateManager[T](HookManager):
    value_proxy: Any
    js_setter: Callable[[T], None]

    def __init__(
        self,
        init_proxy: Any,
        value_proxy: Any,
        js_setter: Callable[[T], None],
    ):
        super().__init__()
        if value_proxy.unwrap() is not init_proxy.unwrap():
            init_proxy.destroy()
        self.value_proxy = value_proxy
        self.js_setter = create_proxy(js_setter)
        self.setter = create_proxy(self.setter)

    def setter(self, new_value: T):
        self.js_setter(create_proxy(new_value))

    def self_cleanup(self):
        # TODO: fix memory leak
        # self.value.destroy()
        # self.js_setter.destroy()
        # self.setter.destroy()
        super().self_cleanup()


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

    _current: T
    
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
        
        :param empty_slice: Must be an empty slice, i.e. when you must
            put a single colon between the square brackets, without any
            numbers.
        :return: The value currently stored in ``self``.
        """
        if empty_slice.start or empty_slice.stop or empty_slice.step:
            raise
        return self._current.unwrap()
    
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

        :param empty_slice: Must be an empty slice, i.e. when you must
            put a single colon between the square brackets, without any
            numbers.
        :param new_value: The new value that should be stored in
            ``self``.

        Once this method has been called, the :class:`Ref <blu.Ref>`\\'s
        stored value will be set to ``new_value``.
        """
        if empty_slice.start or empty_slice.stop or empty_slice.step:
            raise
        try:
            current = self._current
        except AttributeError:
            pass
        else:
            current.destroy()
        self._current = create_proxy(new_value)

    def _cleanup(self):
        try:
            current = self._current
        except AttributeError:
            pass
        else:
            current.destroy()


def use_ref[T](init: T) -> Ref[T]:
    """
    .. include:: /_includes/hook-note.rst

    Store a value doesn't change between renders unless explicitly set
    to a new value.

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
                alert(f'You\'ve clicked the button {count} times.')

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
    manager_in = use_setup(RefManager(ref), True)
    manager_out = useRef(manager_in).current
    # TODO: fix memory leak
    # if manager_in is not manager_out:
    #     manager_in.self_cleanup()
    return manager_out.ref
    

class RefManager[T](HookManager):
    ref: Ref[T] | None = None

    def __init__(self, ref: Ref[T]):
        super().__init__()
        self.ref = create_proxy(ref)

    def self_cleanup(self):
        self.ref._cleanup()
        self.ref.destroy()
        super().self_cleanup()
    
