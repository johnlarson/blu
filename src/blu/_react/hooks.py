from collections.abc import AsyncGenerator, Callable, Generator


def use_effect(
    callback: Callable[[], Generator[None] | AsyncGenerator[None]],
):
    ...


def use_state[T](init: T) -> tuple[T, Callable[[T], None]]:
    ...


class Ref[T]:
    _current: T
    
    def __getitem__(self, empty_slice: slice) -> T:
        if empty_slice.start or empty_slice.stop or empty_slice.step:
            raise
        return self._current
    
    def __setitem__(self, empty_slice: slice, new_value: T):
        if empty_slice.start or empty_slice.stop or empty_slice.step:
            raise
        self._current = new_value


def use_ref[T](init: T) -> Ref[T]:
    ...
