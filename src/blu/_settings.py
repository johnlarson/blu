
from collections.abc import Callable
from dataclasses import dataclass, field, fields
import functools
from typing import Any, cast


@functools.cache
def settings():
    try:
        from app import __settings__  # type: ignore
    except ImportError:
        return Settings()
    else:
        values: dict[str, Any] = {}
        for field in fields(Settings):
            try:
                values[field.name] = getattr(__settings__, field.name)  # type: ignore
            except AttributeError:
                pass
        return Settings(**values)
    

def default[T](factory: Callable[[], Any]):
    return field(default_factory=cast(Callable[[], T], factory))


@dataclass
class Settings:
    
    CLIENT_REQUIREMENTS: list[str] = default(lambda: [])