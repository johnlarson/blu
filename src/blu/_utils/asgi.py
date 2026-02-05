"""
Types based on https://asgi.readthedocs.io/en/latest/specs/www.html
"""

from collections.abc import Iterable
from blu._utils.typing import Any, Literal, NotRequired, Optional, Protocol, TypedDict


class LifespanScopeASGIInfo(TypedDict):
    version: str
    spec_version: NotRequired[str]  # default: '1.0'


class LifespanScope(TypedDict):
    type: Literal["lifespan"]
    asgi: LifespanScopeASGIInfo
    state: NotRequired[
        dict[str, Any]
    ]  # if missing, the server does not support this feature


class ConnectionScopeASGIInfo(TypedDict):
    version: str
    spec_version: NotRequired[Literal["2.0", "2.1", "2.2", "2.3"]]  # default: '2.0'


class ConnectionScope(TypedDict):
    asgi: ConnectionScopeASGIInfo
    path: str
    raw_path: NotRequired[Optional[bytes]]  # default: None
    root_path: NotRequired[str]  # default: ''
    headers: Iterable[tuple[bytes, bytes]]
    client: NotRequired[tuple[str, int]]  # default: None
    server: NotRequired[tuple[str, Optional[int]]]  # default: None
    state: NotRequired[
        dict[str, Any]
    ]  # if missing, the server does not support this feature


class HTTPConnectionScope(ConnectionScope):
    type: Literal["http"]
    http_version: Literal["1.0", "1.1", "2"]
    method: str
    scheme: NotRequired[str]  # default: 'http'. Must not be ''.
    query_string: bytes


class WSConnectionScope(ConnectionScope):
    type: Literal["websocket"]
    http_version: NotRequired[Literal["1.1", "2"]]  # default: '1.1'
    scheme: NotRequired[str]  # default: 'ws'. Must not be ''.
    subprotocols: NotRequired[Iterable[str]]  # default: []
    query_string: NotRequired[Optional[bytes]]  # if missing or None, Default is ''.


type Scope = HTTPConnectionScope | WSConnectionScope | LifespanScope


class LifespanStartupReceiveEvent(TypedDict):
    type: Literal["lifespan.startup"]


class LifespanStartupCompleteSendEvent(TypedDict):
    type: Literal["lifespan.startup.complete"]


class LifespanStartupFailedSendEvent(TypedDict):
    type: Literal["lifespan.startup.failed"]
    message: NotRequired[str]  # default: ''


class LifespanShutdownReceiveEvent(TypedDict):
    type: Literal["lifespan.shutdown"]


class LifespanShutdownCompleteSendEvent(TypedDict):
    type: Literal["lifespan.shutdown.complete"]


class LifespanShutdownFailedSendEvent(TypedDict):
    type: Literal["lifespan.shutdown.failed"]
    message: NotRequired[str]  # default: ''


type LifespanReceiveEvent = (LifespanStartupReceiveEvent | LifespanShutdownReceiveEvent)

type LifespanSendEvent = (
    LifespanStartupCompleteSendEvent
    | LifespanStartupFailedSendEvent
    | LifespanShutdownCompleteSendEvent
    | LifespanShutdownFailedSendEvent
)


class HTTPRequestReceiveEvent(TypedDict):
    type: Literal["http.request"]
    body: NotRequired[bytes]  # default: b''
    more_body: NotRequired[bool]  # default: False


class HTTPDisconnectReceiveEvent(TypedDict):
    type: Literal["http.disconnect"]


type HTTPReceiveEvent = (HTTPRequestReceiveEvent | HTTPDisconnectReceiveEvent)


class WSConnectReceiveEvent(TypedDict):
    type: Literal["websocket.connect"]


class WSReceiveReceiveEvent(TypedDict):
    type: Literal["websocket.receive"]
    bytes: NotRequired[Optional[bytes]]  # default: None
    test: NotRequired[Optional[str]]  # default: None
    # exactly one of bytes or text must be non-None


class WSDisconnectReceiveEvent(TypedDict):
    type: Literal["websocket.disconnect"]
    code: int


type WSReceiveEvent = (
    WSConnectReceiveEvent | WSReceiveReceiveEvent | WSDisconnectReceiveEvent
)


type ReceiveEvent = LifespanReceiveEvent | HTTPReceiveEvent | WSReceiveEvent


class Receiver(Protocol):
    async def __call__(self) -> ReceiveEvent: ...


class HTTPResponseStartSendEvent(TypedDict):
    type: Literal["http.response.start"]
    status: int
    headers: NotRequired[Iterable[tuple[bytes, bytes]]]  # default: []
    trailers: NotRequired[bool]  # default: False


class HTTPResponseBodySendEvent(TypedDict):
    type: Literal["http.response.body"]
    body: NotRequired[bytes]  # default: b''
    more_body: NotRequired[bool]  # default: False


type HTTPSendEvent = HTTPResponseStartSendEvent | HTTPResponseBodySendEvent


class WSAcceptSendEvent(TypedDict):
    type: Literal["websocket.accept"]
    subprotocol: NotRequired[str]  # default: None
    headers: NotRequired[Iterable[tuple[bytes, bytes]]]  # default: []


class WSSendSendEvent(TypedDict):
    type: Literal["websocket.send"]
    bytes: NotRequired[Optional[bytes]]  # default: None
    test: NotRequired[Optional[str]]  # default: None
    # exactly one of bytes or text must be non-None


class WSCloseSendEvent(TypedDict):
    type: Literal["websocket.close"]
    code: NotRequired[int]  # default: 1000
    reason: NotRequired[str]  # if missing or None, default is ''.


type WSSendEvent = WSAcceptSendEvent | WSSendSendEvent | WSCloseSendEvent

type SendEvent = LifespanSendEvent | HTTPSendEvent | WSSendEvent


class Sender(Protocol):
    async def __call__(self, event: SendEvent, /): ...


class App(Protocol):
    async def __call__(self, scope: Scope, receive: Receiver, send: Sender): ...
