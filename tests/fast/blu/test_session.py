import asyncio

import pytest

from tests.utils import ClientFixture, Sender, receive


def _set_cookie_value(set_cookie_headers: list[str], name: str) -> str | None:
    prefix = f"{name}="
    for header in set_cookie_headers:
        cookie_pair = header.split(";", 1)[0]
        if cookie_pair.startswith(prefix):
            return cookie_pair[len(prefix) :]
    return None


def _http_scope(path: str = "/", cookie: str | None = None):
    headers: list[tuple[bytes, bytes]] = []
    if cookie is not None:
        headers.append((b"cookie", cookie.encode("utf-8")))
    if "?" in path:
        path, query_str = path.split("?", 1)
        query = query_str.encode("utf-8")
    else:
        query = b""
    return {
        "asgi": {
            "version": "1",
            "spec_version": "2.0",
        },
        "path": path,
        "headers": headers,
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "query_string": query,
    }


async def test_set_and_get_within_request(client: ClientFixture):
    """
    Values written to the session can be read back during the same
    request.
    """
    c = await client("session")
    response = await c.get("/")
    assert response.headers["X-Count"] == "1"


async def test_persists_across_requests(client: ClientFixture):
    """
    Session data persists across requests for a given user.
    """
    c = await client("session")
    response = await c.get("/")
    assert response.headers["X-Count"] == "1"
    response = await c.get("/")
    assert response.headers["X-Count"] == "2"
    response = await c.get("/getitem")
    assert response.headers["X-Count"] == "2"


async def test_get_returns_none_when_missing(client: ClientFixture):
    """
    session.get(key) returns None when key is not in the session.
    """
    c = await client("session")
    response = await c.get("/get")
    assert response.headers["X-Get-Default"] == "None"


async def test_no_cookie_when_session_empty(client: ClientFixture):
    """
    If nothing has been set on the session, no _blu_session cookie is
    sent in the response.
    """
    c = await client("session")
    response = await c.get("/get")
    assert (
        _set_cookie_value(response.headers.getall("Set-Cookie", []), "_blu_session")
        is None
    )


async def test_get_returns_default_when_missing(client: ClientFixture):
    """
    session.get(key, default) returns default when key is not in the
    session.
    """
    c = await client("session")
    response = await c.get("/get")
    assert response.headers["X-Get-Fallback"] == "fallback"


async def test_get_returns_value_when_present(client: ClientFixture):
    """
    session.get(key) returns the stored value when key is in the
    session.
    """
    c = await client("session")
    await c.get("/")
    response = await c.get("/get")
    assert response.headers["X-Get-Count"] == "1"


async def test_getitem_raises_KeyError_when_missing(patch_app):  # type: ignore
    """
    session[key] raises KeyError when key is not in the session.
    """
    from blu import app

    patch_app("session")
    with pytest.raises(KeyError):
        await app(_http_scope("/missing_key"), receive, Sender())


async def test_SESSION_TIMEOUT_None_never_expires(client: ClientFixture):
    """
    If SESSION_TIMEOUT is None (the default), the session does not time
    out.
    """
    c = await client("session")
    response = await c.get("/")
    assert response.headers["X-Count"] == "1"
    await asyncio.sleep(1.1)
    response = await c.get("/")
    assert response.headers["X-Count"] == "2"


async def test_non_str_key_raises_TypeError(patch_app):  # type: ignore
    """Session keys must be strs."""
    from blu import app

    patch_app("session")
    with pytest.raises(TypeError):
        await app(_http_scope("/non_str_key"), receive, Sender())


async def test_non_json_value_raises_TypeError(patch_app):  # type: ignore
    """Session values must be JSON-serializable."""
    from blu import app

    patch_app("session")
    with pytest.raises(TypeError):
        await app(_http_scope("/non_json_value"), receive, Sender())


async def test_json_serializable_values_round_trip(client: ClientFixture):
    """
    JSON-serializable values such as dicts and lists can be stored in
    the session and read back.
    """
    c = await client("session_json")
    await c.get("/?action=set")
    response = await c.get("/?action=get")
    assert response.headers["X-Data"] == "{'nums': [1, 2], 'ok': True}"
