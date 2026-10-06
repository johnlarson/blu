import base64
from js import document  # type: ignore
import logging
import micropip

import _js_util as _blu_js_utils
from blu._micropython.typing import cast
from blu._micropython.utils import import_module
from blu._mPickle import mpickle as pickle

logging.basicConfig(level=logging.DEBUG)


async def main(packages):
    for package in packages:  # type: ignore
        await micropip.install(package)  # type: ignore
    _blu_js_utils.init(import_module, is_generator)  # type: ignore
    b64_str: str = cast(
        str,
        document.querySelector('script[type="react-data"]').textContent,  # type: ignore
    )
    b64_bytes = b64_str.encode("ascii")
    pickled = base64.b64decode(b64_bytes)
    unpickled = pickle.loads(pickled)  # type: ignore
    _blu_js_utils.renderRoot(unpickled)  # type: ignore


def is_generator(obj):
    return (
        hasattr(obj, "__iter__")
        and hasattr(obj, "__next__")
        and hasattr(obj, "send")
        and hasattr(obj, "throw")
        and hasattr(obj, "close")
    )


__all__ = ["main"]
