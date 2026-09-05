from .utils import type_import as _type_import  # type: ignore


try:
    pass
except ImportError:
    _type_import(
        "typing",
        globals(),
        [
            "Any",
            "Generic",
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
