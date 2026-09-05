from .utils import type_import as _type_import  # type: ignore


if _type_import(
    "collections.abc",
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
):
    pass
