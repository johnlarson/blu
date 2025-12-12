def test_served_from_path_relative_to_app_dir():
    """
    A non-python file under the app/ directory is served from that path
    it is at relative to the app/ directory.
    """
    ...


def test_no_match_404():
    """
    If there is no file available at the request URL, an HTTP 404
    response will be sent.
    """
    ...


def test_dynamic_segments_static_url():
    """
    Even if the static file is under a dynamic segment directory, the
    file can be accessed by an HTTP request whose URL path is the exact
    path to the file, relative to the app/ directory.
    """
    ...


def test_dynamic_segments_dynamic_url_404():
    """
    Even if the static file is under a dynamic segment directory, the
    file cannot be accessed unless the URL path is the exact path to the
    file relative to the app/ directory.
    """
    ...


def test_ignore_python_files():
    """Python files are not served by the static file server."""
    ...