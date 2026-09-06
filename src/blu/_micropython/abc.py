from .utils import type_import as _type_import  # type: ignore


try:
    pass
except ImportError:
    _type_import(
        globals(),
        [
            "Awaitable",
            "AsyncGenerator",
            "AsyncIterable",
            "AsyncIterator",
            "Callable",
            "Coroutine",
            "Generator",
            "Iterable",
            "Iterator",
            "Mapping",
            "Sequence",
        ],
        [],
    )
