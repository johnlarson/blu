
class TypePlaceHolder:
    def __getitem__(self, index):  # type: ignore
        return None


type_place_holder = TypePlaceHolder()

try:
    from typing import *  # type: ignore
except ImportError:
    
    for type_name in [
        'Any',
        'AsyncGenerator',
        'AsyncIterable',
        'AsyncIterator',
        'Callable',
        'Corouotine',
        'Generator',
        'Iterable',
        'Iterator',
        'Literal',
        'Mapping',
        'NotRequired',
        'Optional',
        'Protocol',
        'Sequence',
        'TypedDict',
    ]:
        globals()[type_name] = type_place_holder

    def cast(_, x):  # type: ignore
        return x  # type: ignore