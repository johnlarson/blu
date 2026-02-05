import pytest
from blu._app.router import NotFound
from blu._http import Request
from tests.file_conventions._utils import router


async def test_matching_segment():
    """Should match a segment that equals the directory name."""
    response = await router("literal_segment").handle(Request("/path"))
    assert response._body == "Hello!"  # type: ignore


async def test_leading_underscore():
    """
    A directory with a leading underscore is not treated as a static
    segment.
    """
    with pytest.raises(NotFound):
        await router("leading_underscore").handle(Request("/_path"))


async def test_trailing_underscore():
    """
    A directory with a trailing underscore is not treated as a static
    segment.
    """
    with pytest.raises(NotFound):
        await router("trailing_underscore").handle(Request("/path_"))


async def test_nested():
    """Nested directories are treated as sequential URL segments."""
    r = router("nested_literal_segments")
    response = await r.handle(Request("/path/to/view"))
    assert response._body == "Hello!"  # type: ignore


async def test_has_priority_over_dynamic_segment():
    """
    When both a static segment directory and a dynamic segment directory
    match a segment in a URL, the static segment will be matched.
    """
    r = router("static_dynamic_priority")
    response = await r.handle(Request("/static"))
    assert response._body == "STATIC"  # type: ignore


async def test_top_level_directory():
    """
    A handler file that is the immediate child of the app directory
    matches the URL path /.
    """
    response = await router("top_level_segment").handle(Request("/"))
    assert response._body == "Hello!"  # type: ignore
