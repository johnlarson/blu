from tests.utils import asgi_get


async def test_served_from_path_relative_to_app_dir(patch_app):  # type: ignore
    """
    A non-python file under the app/ directory is served from that path
    it is at relative to the app/ directory.
    """
    patch_app('static_files')
    body = (await asgi_get('/path/to/static/file.txt')).body()
    assert body == 'Hello, World!'


async def test_no_match_404(patch_app):  # type: ignore
    """
    If there is no file available at the request URL, an HTTP 404
    response will be sent.
    """
    patch_app('static_files')
    sender = await asgi_get('/wrong/path/to/file.txt')
    assert next(sender).get('status', None) == 404
    assert sender.body() == 'Not found: /wrong/path/to/file.txt'


async def test_dynamic_segments_static_url(patch_app):  # type: ignore
    """
    Even if the static file is under a dynamic segment directory, the
    file can be accessed by an HTTP request whose URL path is the exact
    path to the file, relative to the app/ directory.
    """
    patch_app('static_files_dynamic_path')
    body = (await asgi_get('/_a_/file.txt')).body()
    assert body == 'Hello, World!'


async def test_dynamic_segments_dynamic_url_404(patch_app):  # type: ignore
    """
    Even if the static file is under a dynamic segment directory, the
    file cannot be accessed unless the URL path is the exact path to the
    file relative to the app/ directory.
    """
    patch_app('static_files_dynamic_path')
    sender = await asgi_get('/foo/file.txt')
    assert next(sender).get('status', None) == 404
    assert sender.body() == 'Not found: /foo/file.txt'


async def test_py_file(patch_app):  # type: ignore
    """Trying to access a .py file will result in a 404."""
    patch_app('client_module')
    sender = await asgi_get('/module.py')
    assert next(sender).get('status', None) == 404
    assert sender.body() == 'Not found: /module.py'