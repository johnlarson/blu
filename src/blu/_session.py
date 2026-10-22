from contextvars import ContextVar, Token
from dataclasses import dataclass, field
import json

from itsdangerous import BadData, URLSafeTimedSerializer

from blu._micropython.typing import Any
from blu._settings import settings

COOKIE_NAME = "_blu_session"


@dataclass
class _SessionState:
    data: dict[str, Any] = field(default_factory=dict)
    modified: bool = False


_current: ContextVar[_SessionState | None] = ContextVar("blu_session", default=None)


class Session:
    """
    Per-user data that persists across requests.

    Access the current request's session via :data:`blu.session`:

    .. code-block:: python

        from blu import session


        def __page__():
            session['a'] = 1
            return 'Hello'

    Keys must be :class:`str`\\ s, and values must be JSON-serializable.

    .. warning::

       Do not include any sensitive data in the session, as it can be
       read by the client.

    In order to use sessions, ``__settings__.py`` must have a
    ``SECRET_KEY`` setting. See
    :ref:`api-reference/file-conventions:__settings__.py`.
    """

    def _state(self) -> _SessionState:
        state = _current.get()
        if state is None:
            raise RuntimeError("No active request session")
        return state

    def __getitem__(self, key: str) -> Any:
        """
        Return the value associated with ``key``.

        :param key: A session key.
        :return: The value associated with ``key``.
        :raises KeyError: If ``key`` is not in the session.
        """
        self._require_secret_key()
        return self._state().data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Store ``value`` under ``key``.

        :param key: A session key. Must be a :class:`str`.
        :param value: A JSON-serializable value.
        """
        self._require_secret_key()
        if not isinstance(key, str):
            raise TypeError("Session keys must be str")
        try:
            json.dumps(value)
        except (TypeError, ValueError) as e:
            raise TypeError("Session values must be JSON-serializable") from e
        state = self._state()
        state.data[key] = value
        state.modified = True

    def get[T](self, key: str, default: T = None) -> Any | T:
        """
        Return the value for ``key`` if it is in the session, else
        ``default``.

        Like :meth:`dict.get`.

        .. code-block:: python

            session.get('a')  # None if 'a' is not in the session
            session.get('a', 0)  # 0 if 'a' is not in the session

        :param key: A session key.
        :param default: A value to return if ``key`` is not in the
            session. Defaults to ``None``.
        :return: The value associated with ``key``, or ``default`` if
            ``key`` is not in the session.
        """
        self._require_secret_key()
        return self._state().data.get(key, default)

    def _require_secret_key(self) -> None:
        if settings().SECRET_KEY is None:
            raise RuntimeError(
                "Sessions require a SECRET_KEY setting in __settings__.py"
            )


session = Session()
"""The :class:`~blu.Session` for the current request."""


def bind_session(cookie_header: str | None) -> Token[_SessionState | None]:
    """Load the session from the Cookie header and bind it for this request."""
    return _current.set(_load_session_state(cookie_header))


def unbind_session(token: Token[_SessionState | None]) -> None:
    _current.reset(token)


def session_cookie_header() -> str | None:
    """
    Return a ``Set-Cookie`` header value for the current session, or
    ``None`` if no cookie should be sent.

    No cookie is sent when the session is empty (nothing has been set).
    """
    state = _current.get()
    if state is None or not state.modified or not state.data:
        return None
    secret_key = settings().SECRET_KEY
    if secret_key is None:
        return None
    serializer = URLSafeTimedSerializer(secret_key)
    value = serializer.dumps(state.data)
    return f"{COOKIE_NAME}={value}; Path=/"


def _load_session_state(cookie_header: str | None) -> _SessionState:
    secret_key = settings().SECRET_KEY
    if secret_key is None or not cookie_header:
        return _SessionState()
    raw = _get_cookie(cookie_header, COOKIE_NAME)
    if raw is None:
        return _SessionState()
    serializer = URLSafeTimedSerializer(secret_key)
    max_age = settings().SESSION_TIMEOUT
    try:
        data = serializer.loads(raw, max_age=max_age)
    except BadData:
        return _SessionState()
    if not isinstance(data, dict):
        return _SessionState()
    return _SessionState(data={str(k): v for k, v in data.items()})


def _get_cookie(cookie_header: str, name: str) -> str | None:
    for part in cookie_header.split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        if key.strip() == name:
            return value.strip()
    return None
