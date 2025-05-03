from collections.abc import AsyncGenerator, Callable, Generator


type Effect = Callable[[], Generator[None] | AsyncGenerator[None]]


def use_effect(callback: Effect):
    ...


def use_state[T](init: T) -> tuple[T, Callable[[T], None]]:
    ...


class Ref[T]:
    _current: T
    
    def __getitem__(self, empty_slice: slice) -> T:
        if empty_slice.start or empty_slice.stop or empty_slice.step:
            raise
        return self._current


def use_ref[T](init: T) -> Ref[T]:
    ...
