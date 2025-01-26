from blu._utils import asgi


import functools
import os
from blu._app import Blu
from blu._utils import asgi


class DefaultApp:
    _project_dir: str

    def __init__(self):
        self._project_dir = os.getcwd()

    async def __call__(
        self,
        scope: asgi.Scope,
        receive: asgi.Receiver,
        send: asgi.Sender,
    ):
        inner_app = self._get_inner_app()
        return await inner_app(scope, receive, send)
    
    @functools.cache
    def _get_inner_app(self) -> asgi.App:
        return Blu('app', self._project_dir)
    

app = DefaultApp()