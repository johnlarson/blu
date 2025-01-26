from collections.abc import Iterable, Mapping
import json

from blu._utils.asyncio import io_bound


type JsonData = (
    None |
    bool |
    int |
    float |
    str |
    Iterable['JsonData'] |
    Mapping[str, 'JsonData']
)


@io_bound
def loads(json_string: str) -> JsonData:
    return json.loads(json_string)


@io_bound
def dumps(json_data: JsonData) -> str:
    return json.dumps(json_data)