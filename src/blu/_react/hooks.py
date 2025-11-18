from collections.abc import AsyncGenerator, Callable, Generator


def use_effect(
    callback: Callable[
        [],
        None | Generator[None] | AsyncGenerator[None],
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

        @client
        def MyClientElement():
            
            @use_effect
            def setup_and_teardown():
                do_some_setup()
                yield
                do_some_teardown()

            return div['Hello!']
    """
    ...


def use_state[T](init: T) -> tuple[T, Callable[[T], None]]:
    """
    .. include:: /_includes/hook-note.rst
    """
    ...


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
            from blu.tml import button

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
    """
    ...
