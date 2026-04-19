from blu._http import Request

from tests.fast.file_conventions._utils import router


async def test_matches_arbitrary_segment():
    """A dynamic segment directory matches any URL segment."""
    response = await router("dynamic_segment").handle(Request("/anything"))
    assert response._body == "Hi."  # type: ignore


async def test_nested():
    """Works when nested in another dynamic segment directory."""
    response = await router("nested_dynamic_segments").handle(Request("/a/b"))
    assert response._body == "Hi!"  # type: ignore


async def test_nested_with_static_segment():
    """
    Works when nested in both static and dynamic segment directories.
    """
    r = router("static_dynamic_nested")
    response = await r.handle(Request("/static/foo"))
    assert response._body == "Nested."  # type: ignore


async def test_multiple_dynamic_segments():
    """
    If there are two dynamic segment directories, and only one leads to
    a full match with the URL, that one will be used.
    """
    response = await router("multiple_dynamic").handle(Request("/foo/d"))
    assert response._body == "_c_/d"  # type: ignore


async def test_with_non_matching_static_segment():
    """
    Works when there is a non-matching static segment directory at the
    same level.
    """
    r = router("dynamic_non_matching_static")
    response = await r.handle(Request("/blah"))
    assert response._body == "DYNAMIC"  # type: ignore


async def test_with_static_segment_with_no_full_match():
    """
    Works when at the same level as a static segment directory that
    doesn't lead to a full match with the URL being processed.
    """
    r = router("dynamic_static_not_full_match")
    response = await r.handle(Request("/foo/bar"))
    assert response._body == "_dynamic_/bar"  # type: ignore
