def test_full_match():
    """
    If the path to __index__.py is a full match for the current URL, the
    value returned by its __page__ function will be loaded in the user's
    browser.
    """
    ...


def test_matches_start_only_no_match():
    """
    A URL that only contains part of the path to an __index__.py file
    does not result that __index__.py file being used.
    """
    ...


def test_last_segment_different_no_match():
    """
    A URL that almost matches the path to an __index__.py file only the
    last segment is different does not result in that __index__.py file
    being used.
    """
    ...


def test_extra_segments_no_match():
    """
    A URL that includes the path to an __index__.py file but also
    contains extra segments after does not result in that __index__.py
    file being used.
    """
    ...


def test_handler_return_response():
    """
    If the __page__ function returns a blu.Response object, the HTTP
    response sent to the client will have the body, status code, and
    headers set in the Response object.
    """
    ...


def test_handler_handles_route_params():
    """
    Route params are passed into the 
    """
    ...


def test_handler_handles_query_params():
    """
    
    """
    ...


