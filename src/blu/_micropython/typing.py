from .utils import type_import as _type_import  # type: ignore


try:
    from typing import *  # fmt: skip
except ImportError:
    _type_import(
        globals(),
        [
            "Any",
            "IO",
            "List",
            "Literal",
            "NotRequired",
            "Optional",
            "ParamSpec",
            "TypeAlias",
            "TypeVar",
            "Union",
        ],
        [
            "Protocol",
            "TypedDict",
        ],
    )

    def cast(_, x):  # type: ignore
        return x  # type: ignore

    class _GenericClass:
        def __getitem__(self, _):
            return object

    Generic = _GenericClass()
