from blu import Response
from blu.html import div


def test_sets_page_body_positional():
    """Sets body to the first positional argument in __init__."""
    assert Response(div)._body == div  # type: ignore


def test_sets_page_body_kw():
    """
    Allows setting body with the "body" keyword argument in __init__.
    """
    assert Response(body=div)._body == div  # type: ignore


def test_sets_http_status_positional():
    """
    Sets HTTP status to the second positional argument in __init__.
    """
    assert Response(None, 404)._status == 404  # type: ignore


def test_sets_http_status_kw():
    """
    Allows setting HTTP status with the "status" keyword argument in
    __init__.
    """
    assert Response(status=404)._status == 404  # type: ignore


def test_sets_headers_positional():
    """Sets HTTP headers to third positional argument in __init__."""
    assert Response(None, 200, {'A': 'b'})._headers == {'A': 'b'}  # type: ignore


def test_sets_headers_kw():
    """
    Allows setting HTTP headers with "headers" keyword argument in
    __init__.
    """
    assert Response(headers={'A': 'b'})._headers == {'A': 'b'}  # type: ignore


def test_body_status_and_headers():
    """
    Correctly sets body, status and headers when all are passed into
    __init__.
    """
    response = Response(div, status=401, headers={'A': 'a'})
    assert response._body == div  # type: ignore
    assert response._status == 401  # type: ignore
    assert response._headers == {'A': 'a'}  # type: ignore


def test_body_default_none():
    """Response body defaults to None."""
    assert Response()._body == None  # type: ignore
    

def test_status_default_200():
    """Response status defaults to 200."""
    assert Response()._status == 200  # type: ignore


def test_headers_default_empty_dict():
    """Response headers default to {}."""
    assert Response()._headers == {}  # type: ignore.