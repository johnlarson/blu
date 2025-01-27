from blu._http import Request, Response


class Router:
    
    def __init__(self, app_module: str):
        ...

    async def handle(self, request: Request) -> Response:
        ...