from tempfile import TemporaryDirectory
from blu._utils.typing import Optional

from blu._app_old import Blu
from blu._utils import asgi


inner_app: Optional[Blu] = None


async def get_inner_app() -> Blu:
    # Add to global scope to make sure it doesn't get garbage-collected.
    # (If the context mananager's underlying async generator gets
    # garbage-collected, 
    global context_manager
    with TemporaryDirectory() as project_dir:
        context_manager = Blu('app', project_dir).dev()
        return await context_manager.__aenter__()


async def app(scope: asgi.Scope, receive: asgi.Receiver, send: asgi.Sender):
    global inner_app
    if inner_app is None:
        inner_app = await get_inner_app()
    return await inner_app(scope, receive, send)