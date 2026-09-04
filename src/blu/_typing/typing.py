from .utils import type_import as _type_import  # type: ignore


if _type_import(
    "typing",
    globals(),
    [
        "Any",
        "Literal",
        "NotRequired",
        "Optional",
    ],
    [
        "Protocol",
        "TypedDict",
    ],
):

    def cast(_, x):  # type: ignore
        return x  # type: ignore
