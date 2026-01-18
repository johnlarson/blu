import pytest
from blu._app.router import NotFound
from blu._http import Request
from tests.file_conventions._utils import router


async def test_full_match():
    """
    If the path to __index__.py is a full match for the current URL, the
    value returned by its __page__ function will be loaded in the user's
    browser.
    """
    r = router('index_abc')
    response = await r.handle(Request('/a/b/c'))
    assert response._body == 'Match!'  # type: ignore


async def test_matches_start_only_no_match():
    """
    A URL that only contains part of the path to an __index__.py file
    does not result that __index__.py file being used.
    """
    with pytest.raises(NotFound):
        await router('index_abc').handle(Request('/a/b'))


async def test_last_segment_different_no_match():
    """
    A URL that almost matches the path to an __index__.py file only the
    last segment is different does not result in that __index__.py file
    being used.
    """
    with pytest.raises(NotFound):
        await router('index_abc').handle(Request('/a/b/foo'))


async def test_extra_segments_no_match():
    """
    A URL that includes the path to an __index__.py file but also
    contains extra segments after does not result in that __index__.py
    file being used.
    """
    with pytest.raises(NotFound):
        await router('index_abc').handle(Request('/a/b/c/foo'))


async def test_handler_return_response():
    """
    If the __page__ function returns a blu.Response object, the HTTP
    response sent to the client will have the body, status code, and
    headers set in the Response object.
    """
    r = router('index_response')
    response = await r.handle(Request('/'))
    assert response._body == 'body'  # type: ignore
    assert response._status == 401  # type: ignore
    assert response._headers == {'Name': 'value'}  # type: ignore


async def test_handler_only_route_params():
    """
    If / does not appear in the handler call signature, each argument
    will capture the value of the dynamic segment whose name matches the
    argument name.
    """
    r = router('index_dynamic_abc')
    response = await r.handle(Request('/1/2/3'))
    assert response._body == ('1', '2', '3')  # type: ignore


async def test_nonexistent_route_params():
    """
    If there are route parameters in the handler's call signature whose
    names don't match those of any of the dynamic segment matched by the
    handler's filesystem location, a TypeError will be thrown when the
    route is accessed through HTTP.
    """
    with pytest.raises(TypeError):
        await router('index_extra_route_params').handle(Request('/'))


async def test_missing_route_params():
    """
    If there are dynamic segments matched by the handler's filesystem
    location that don't have a corresponding argument in the handler's
    call signature, the handler will still be called with the route
    parameter argument(s) that it allows.
    """
    ...


async def test_single_underscore():
    """
    If there are no positional-only arguments in the __page__ handler's
    call signature, an argument whose name is _ (single underscore) will
    have a value of None when the handler is called.
    """
    ...


async def test_handler_only_query_params():
    """
    If the handler's call signature starts with an argument called "__",
    then when the handler is matched, it will be called, passing in the
    query parameters as keyword arguments, where the query parameter
    name is the argument key, and the query parameter value is the
    argument value.
    """
    ...


async def test_nonexistent_query_params():
    """
    If a handler's call signature includes query parameters that are not
    provided in the request URL and the call signature does not provide
    default values for those query parameters, a TypeError will be
    raised.
    """
    ...


async def test_query_param_default_values():
    """
    If a handler's call signature includes query parameters that are not
    provided in the request URL but the call signature does provide
    default values for those query parameters, the handler will be run
    with those query parameter arguments' default values.
    """
    ...


async def test_query_params_not_in_call_signature():
    """
    Any query parameters in the URL that are not captured in the call
    signature of the __page__ handler are be ignored.
    """
    ...


async def test_query_params_kwargs():
    """
    Query parameters can be captured using keyword argument unpacking.
    """
    ...


async def test_handler_route_and_query_params():
    """
    If a __page__ handler has the argument "__" in its call signature,
    arguments on the left will be treated as route parameters, and
    arguments on the right of it will be treated as query parameters.
    """
    ...


async def test_pos_only_single_underscore():
    """
    A positional-only argument whose name is _ (single underscore) will
    have a value of None when the handler is called.
    """
    ...


async def test_async_handler():
    """__page__ handler can be an async function."""
    ...