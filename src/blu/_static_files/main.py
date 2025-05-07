print('Hello, World!')


import asyncio
from typing import Any, cast

from js import document, JSON  # type: ignore
from pyscript import js_import  # type: ignore

react_dom = cast(Any, js_import('https://esm.sh/react-dom/client'))
react = cast(Any, js_import('https://esm.sh/react'))

async def main():
    json_str = document.querySelector('script[type="react-data"]').textContent  # type: ignore
    root_node_json = JSON.parse(json_str)  # type: ignore
    root_node = get_node(root_node_json)
    # import_promises = get_import_promises(root_node_json)
    # imports = await asyncio.gather(import_promises)
    # root_node = get_node(root_node_json, imports)
    if root_node_json['tagname'] == 'html':
        react_dom.createRoot(document).render(root_node)
    else:
        react_dom.createRoot(document.body).render(root_node)  # type: ignore


def get_node(json: Any):
    ...


def get_obj(obj: Any):
    ...


def get_array(array: Any):
    ...


await main()