from collections.abc import Iterable, Mapping
import json

from blu._utils.asyncio import io_bound

from blu._utils.client import is_client

type JsonData = (
    None | bool | int | float | str | Iterable["JsonData"] | Mapping[str, "JsonData"]
)


if is_client:

    from js import JSON  # type: ignore

    async def loads(json_string: str) -> JsonData:  # type: ignore
        return JSON.parse(json_string)  # type: ignore

    async def dumps(json_data: JsonData) -> str:  # type: ignore
        return JSON.stringify(json_data)  # type: ignore

else:

    @io_bound
    def loads(json_string: str) -> JsonData:
        return json.loads(json_string)

    @io_bound
    def dumps(json_data: JsonData) -> str:
        return json.dumps(json_data)
