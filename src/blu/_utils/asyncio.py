import asyncio
import functools

from blu._exceptions import WrongEnvironmentError
from blu._micropython.abc import Awaitable, Callable, Coroutine
from blu._micropython.typing import Any, IO, TypeVar, ParamSpec, Union, cast
from blu._utils.client import is_client

if not is_client:
    from concurrent.futures import Executor, ProcessPoolExecutor, ThreadPoolExecutor
else:
    from blu._micropython.utils import _TypeStub

    Executor = _TypeStub()
    ProcessPoolExecutor = _TypeStub()
    ThreadPoolExecutor = _TypeStub()

T = TypeVar("T")
P = ParamSpec("P")
R = TypeVar("R")
IOType = TypeVar("IOType", bound=Union[IO[str], IO[bytes]])
IOContentType = TypeVar("IOContentType", bound=Union[str, bytes])


async def awaitable(input: T | Awaitable[T]) -> T:
    if isinstance(input, Awaitable):
        return await cast(Awaitable[T], input)
    else:
        return input


def to_sync(fn: Callable[P, Coroutine[Any, Any, R]]) -> Callable[P, R]:
    def ret(*args: P.args, **kwargs: P.kwargs) -> R:
        return asyncio.run(fn(*args, **kwargs))

    return ret


def io_bound(
    fn: Callable[P, R],
) -> Callable[P, Coroutine[Any, Any, R]]:
    return _asyncify(fn, ThreadPoolExecutor)  # type: ignore


def cpu_bound(
    fn: Callable[P, R],
) -> Callable[P, Coroutine[Any, Any, R]]:
    return _asyncify(fn, ProcessPoolExecutor)  # type: ignore


def _asyncify(
    fn: Callable[P, R], executor: type[Executor]
) -> Callable[P, Awaitable[R]]:  # type: ignore
    async def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
        if is_client:
            raise WrongEnvironmentError(
                f"{fn} can only be called in a server environment."
            )
        loop = asyncio.get_running_loop()
        bound = functools.partial(fn, *args, **kwargs)
        with executor() as pool:  # type: ignore
            return await loop.run_in_executor(pool, bound)

    return wrapped
