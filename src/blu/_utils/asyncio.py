import asyncio
from collections.abc import Awaitable, Callable, Coroutine
from concurrent.futures import Executor, ProcessPoolExecutor, ThreadPoolExecutor
import functools
from typing import Any


def syncify[**P, R](fn: Callable[P, Coroutine[Any, Any, R]]) -> Callable[P, R]:
    def ret(*args: P.args, **kwargs: P.kwargs) -> R:
        return asyncio.run(fn(*args, **kwargs))
    return ret


def io_bound[**P, R](fn: Callable[P, R]) -> Callable[P, Awaitable[R]]:
    return asyncify(fn, ThreadPoolExecutor)


def cpu_bound[**P, R](fn: Callable[P, R]) -> Callable[P, Awaitable[R]]:
    return asyncify(fn, ProcessPoolExecutor)


def asyncify[**P, R](
    fn: Callable[P, R], executor: type[Executor]
) -> Callable[P, Awaitable[R]]:
    async def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
        loop = asyncio.get_running_loop()
        bound = functools.partial(fn, *args, **kwargs)
        with executor() as pool:
            return await loop.run_in_executor(pool, bound)
    return wrapped