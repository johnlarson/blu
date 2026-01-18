import pytest
from blu import Response
from blu._app.router import NotFound
from blu._http import Request
from blu.html import div
from tests.file_conventions._utils import router


async def test_full_match():
    """
    If the path to __default__.py is a full match for the current URL,
    the value returned by its __page__ function will be loaded in the
    user's browser.
    """
    response = await router('default_full_match').handle(Request('/a/foo/c'))
    assert response._body == 1  # type: ignore


async def test_matches_when_one_extra_segment():
    """
    A URL that includes the path to an __default__.py file and contains
    an extra segment results in the file's __page__ handler being used.
    """
    response = await router('default_extra_segment').handle(Request('/a/b'))
    assert response._body == 'DEFAULT'  # type: ignore


async def test_matches_when_multiple_extra_segments():
    """
    A URL that includes the path to an __default__.py file and contains
    multiple extra segments results in the file's __page__ handler being
    used.
    """
    r = router('default_extra_segment')
    response = await r.handle(Request('/a/b/c/d'))
    assert response._body == 'DEFAULT'  # type: ignore


async def test_matches_start_only_no_match():
    """
    A URL that only contains part of the path to an __default__.py file
    does not result that __index__.py file being used.
    """
    with pytest.raises(NotFound):
        await router('default_incomplete_match').handle(Request('/a/b'))


async def test_last_filepath_segment_different_no_match():
    """
    A URL that almost matches the path to a __default__.py file only the
    last segment is different does not result in that __default__.py
    file being used.
    """
    with pytest.raises(NotFound):
        await router('default_one_segment_off').handle(Request('/a/b/foo'))


async def test_only_matches_if_no_other_match():
    """
    If there's an __index__.py file under a more specific path that
    matches the URL, the __index__.py file will be used instead.
    """
    response = await router('index_file_priority').handle(Request('/foo/c'))
    assert response._body == 'INDEX'  # type: ignore


async def test_more_specific_default_file():
    """
    If there's another __default__.py file under a more specific path
    that matches the URL, that other __default__.py file will be used
    instead.
    """
    r = router('default_specific_priority')
    response = await r.handle(Request('/foo/c'))
    assert response._body == 'MORE SPECIFIC'  # type: ignore


async def test_handler_return_response():
    """
    If the __page__ function returns a blu.Response object, the HTTP
    response sent to the client will have the body, status code, and
    headers set in the Response object.
    """
    response = await router('default_response_ret').handle(Request('/'))
    assert response._body == 'BODY'  # type: ignore
    assert response._status == 401  # type: ignore
    assert response._headers == {'A': 'b'}  # type: ignore


async def test_handler_only_route_params():
    """
    If / does not appear in the handler call signature, each argument
    will capture the value of the dynamic segment whose name matches the
    argument name.
    """
    response = await router('default_route_params').handle(Request('/1/2/3'))
    assert response._body == ('1', '2', '3')  # type: ignore


async def test_path_param():
    """
    If / does not appear in the handler call signature and there is an
    argument name with a double trailing underscore, that argument will
    be populated with the remaining path, with no leading or trailing
    slash.
    """
    response = await router('default_path_param').handle(Request('/1/2/3'))
    assert response._body == '1/2/3'  # type: ignore


async def test_single_underscore_arg():
    """
    If / does not appear in the handler call signature and there is an
    argument whose name is a single underscore, that argument will be
    set to None.
    """
    response = await router('default_single_underscore').handle(Request('/'))
    assert response._body == None  # type: ignore


async def test_nonexistent_route_params():
    """
    If there are route parameters in the handler's call signature whose
    names don't match those of any of the dynamic segment matched by the
    handler's filesystem location, a TypeError will be thrown when the
    route is accessed through HTTP.
    """
    with pytest.raises(TypeError):
        await router('def_extra_route_params').handle(Request('/'))


async def test_missing_route_params():
    """
    If there are dynamic segments matched by the handler's filesystem
    location that don't have a corresponding argument in the handler's
    call signature, the handler will still be called with the route
    parameter argument(s) that it allows.
    """
    r = router('def_missing_route_params')
    response = await r.handle(Request('/1/2/3'))
    assert response._body == '2'  # type: ignore


async def test_handler_query_params():
    """
    If the handler has positional-only and positional/keyword arguments,
    then when the handler is matched, it will be called, passing in the
    query parameters as positional/keyword arguments, where the query
    parameter name is the argument key, and the query parameter value is
    the argument value.
    """
    response = await router('def_query').handle(
        Request('/', query={'a': '1', 'b': '2', 'c': '3'}),
    )
    assert response._body == ('1', '2', '3')  # type: ignore


async def test_nonexistent_query_params():
    """
    If a handler's call signature includes query parameters that are not
    provided in the request URL and the call signature does not provide
    default values for those query parameters, a TypeError will be
    raised.
    """
    with pytest.raises(TypeError):
        await router('def_extra_route_params').handle(Request('/'))


async def test_query_param_default_values():
    """
    If a handler's call signature includes query parameters that are not
    provided in the request URL but the call signature does provide
    default values for those query parameters, the handler will be run
    with those query parameter arguments' default values.
    """
    r = router('def_query_params_default')
    response = await r.handle(Request('/'))
    assert response._body == 3  # type: ignore


async def test_query_params_not_in_call_signature():
    """
    Any query parameters in the URL that are not captured in the call
    signature of the __page__ handler are ignored.
    """
    r = router('def_missing_query_params')
    response = await r.handle(Request('/', query={'a': '1', 'b': '2'}))
    assert response._body == 25  # type: ignore


async def test_query_params_kwargs():
    """
    Query parameters can be captured using keyword argument unpacking.
    """
    r = router('def_query_kwarg')
    response = await r.handle(Request('/', query={'a': '1', 'b': '2'}))
    assert response._body == ('1', '2')  # type: ignore



def test_handler_route_and_query_params():
    """
    If a __page__ handler has a / in its call signature, arguments on
    the left will be treated as route parameters, and arguments on the
    right of it will be treated as query parameters.
    """
    ...


def test_pos_only_path_param():
    """
    If a __page__ handler has positional-only arguments, and one of
    those has a trailing double underscore in its name, that argument
    will be populated with the remaining portion of the path that is not
    matched by the __default__.py file where __page__ is, without a
    leading or trailing /.
    """
    ...


def test_pos_only_single_underscore():
    """
    If a __page__ handler has positional-only arguments, and one of
    those is named _ (single underscore), then that argument's value
    will be set to None when __page__ is called.
    """
    ...


def test_handler_dunder_is_empty_string():
    """
    If a __page__ handler has the argument "__" in its call signature,
    the value of "__" will be the remaining, unmatched portion of the
    URL, without an initial or trailing /.
    """
    ...

