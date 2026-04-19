import asyncio
from collections.abc import Awaitable, Callable, Coroutine
import functools

from blu._utils.typing import Any, cast
from blu._utils.client import is_client, WrongEnvironmentError

if not is_client:
    from concurrent.futures import Executor, ProcessPoolExecutor, ThreadPoolExecutor
else:
    from blu._utils.typing import type_place_holder

    Executor = type_place_holder
    ProcessPoolExecutor = type_place_holder
    ThreadPoolExecutor = type_place_holder


async def awaitable[T](input: T | Awaitable[T]) -> T:
    if isinstance(input, Awaitable):
        return await cast(Awaitable[T], input)
    else:
        return input


def to_sync[**P, R](fn: Callable[P, Coroutine[Any, Any, R]]) -> Callable[P, R]:
    def ret(*args: P.args, **kwargs: P.kwargs) -> R:
        return asyncio.run(fn(*args, **kwargs))

    return ret


def io_bound[
    **P, R
](fn: Callable[P, R],) -> Callable[P, Coroutine[Any, Any, R]]:
    return _asyncify(fn, ThreadPoolExecutor)  # type: ignore


def cpu_bound[
    **P, R
](fn: Callable[P, R],) -> Callable[P, Coroutine[Any, Any, R]]:
    return _asyncify(fn, ProcessPoolExecutor)  # type: ignore


def _asyncify[
    **P, R
](fn: Callable[P, R], executor: type[Executor]) -> Callable[  # type: ignore
    P, Awaitable[R]
]:
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
