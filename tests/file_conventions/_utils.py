import importlib
from blu._app.router import Router, router_from_root_package


def router(module_name: str) -> Router:
    module = importlib.import_module(f'tests.apps.{module_name}')
    return router_from_root_package(module)