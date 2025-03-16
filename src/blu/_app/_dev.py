from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager


@asynccontextmanager
async def watch_build() -> AsyncGenerator[None]:
    yield