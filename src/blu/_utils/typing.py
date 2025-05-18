try:
    from typing import *  # type: ignore
except ImportError:

    class TypePlaceHolder:
        def __getitem__(self, index):  # type: ignore
            return None
    
    type_place_holder = TypePlaceHolder()
    
    def type_place_holder_generator():
        yield type_place_holder

    (
        Any,
        AsyncGenerator,
        AsyncIterable,
        AsyncIterator,
        Callable,
        Corouotine,
        Generator,
        Iterable,
        Iterator,
        Literal,
        Mapping,
        NotRequired,
        Optional,
        Protocol,
        Sequence,
        TypedDict,
    ) = type_place_holder_generator()

    def cast[T](_, x: T) -> T:
        return x