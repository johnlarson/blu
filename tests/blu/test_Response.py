def test_sets_page_body_positional():
    """Sets body to the first positional argument in __init__."""
    ...


def test_sets_page_body_kw():
    """
    Allows setting body with the "body" keyword argument in __init__.
    """
    ...


def test_sets_http_status_positional():
    """
    Sets HTTP status to the second positional argument in __init__.
    """
    ...


def test_sets_http_status_kw():
    """
    Allows setting HTTP status with the "status" keyword argument in
    __init__.
    """
    ...


def test_sets_headers_positional():
    """Sets HTTP headers to third positional argument in __init__."""
    ...


def test_sets_headers_kw():
    """
    Allows setting HTTP headers with "headers" keyword argument in
    __init__.
    """
    ...


def test_body_status_and_headers():
    """
    Correctly sets body, status and headers when all are passed into
    __init__.
    """
    ...