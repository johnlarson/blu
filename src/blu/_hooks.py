from collections.abc import AsyncGenerator, Callable, Generator
from typing import Any
from react import useEffect, useState, useRef


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
    manager = EffectManager().use_setup()
    manager.callback = callback
    useEffect(manager.js_callback)
    manager.use_teardown()


class HookManager:
    self_effect: Callable[[], None | Callable[[], None]]
    self_cleanup: Callable[[], None]

    def use_setup(self):
        from pyscript.ffi import create_proxy
        proxy_pre_ref = create_proxy(self)
        proxy = useRef(proxy_pre_ref).current
        if proxy_pre_ref is not proxy:
            proxy_pre_ref.destroy()
        def drop_refs_effect():
            def cleanup():
                proxy.destroy()
            self.self_cleanup = cleanup
        self.self_effect = useRef(drop_refs_effect).current
        return proxy

    def use_teardown(self):
        useEffect(self.self_effect, [])

    


class EffectManager(HookManager):
    callback: Callable[callback: Callable[[], None | Generator[None]]] | None = None
    generator: Generator[None] | None = None

    def js_callback(self):
        self.generator = self.callback()
        return self.js_cleanup
    
    def js_cleanup(self):
        if self.generator is not None:
            try:
                next(self.generator)
            except StopIteration:
                pass


def _use_drop_refs_effect(no_gc: list[Any]):
    def drop_refs_effect():
        def cleanup():
            no_gc.destroy()
        no_gc.append(cleanup)
    drop_refs_effect_ref = useRef(drop_refs_effect)
    no_gc.add(drop_refs_effect_ref.current)
    useEffect(drop_refs_effect_ref.current, [])


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
    manager = StateManager().use_setup()
    value, js_setter = useState(init)
    manager.value = value
    manager.js_setter = js_setter
    manager.use_teardown()
    return manager.value, manager.setter


class StateManager[T](HookManager):
    value: T
    js_setter: Callable[[T], None]

    def setter(self, new_value: T):
        self.value = new_value
        self.js_setter(new_value)


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
        return self._current
    
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
        self._current = new_value


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
    manager = RefManager().use_setup()
    ref_in: Ref[T] = Ref()
    ref_in[:] = init
    ref: Ref[T] = useRef(ref_in).current
    manager.ref = ref
    manager.use_teardown()
    return ref
    

class RefManager[T](HookManager):
    ref: Ref[T] | None = None

