from .utils import type_import as _type_import


if _type_import(
    "collections.abc",
    globals(),
    [
        "AsyncGenerator",
        "AsyncIterable",
        "AsyncIterator",
        "Callable",
        "Corouotine",
        "Generator",
        "Iterable",
        "Iterator",
        "Mapping",
        "Sequence",
    ],
    [],
):
    pass
