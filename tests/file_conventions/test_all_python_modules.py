from tests.utils import asgi_get


async def test_client_modules(patch_app):  # type: ignore
    """
    Any python module under the app package for which
    module.__client__ == True will be available client-side.
    """
    patch_app('client_module')
    body = (await asgi_get('/_blu_internal/app_module/module')).body()
    assert body == '__client__ = True\n\nA = 3'


async def test_no_client_marker(patch_app):  # type: ignore
    """
    Any python module under the app package for which module.__client__
    is not set will be unavailable client-side.
    """
    patch_app('basic')
    sender = await asgi_get('/_blu_internal/app_module/__index__')
    headers = next(sender)
    assert headers.get('status', None) == 404
    assert sender.body() == ''


async def test_client_not_true(patch_app):  # type: ignore
    """
    Any python module under the app package for which module.__client__
    is not True will be unavailable client-side.
    """
    patch_app('client_false')
    sender = await asgi_get('/_blu_internal/app_module/module')
    headers = next(sender)
    assert headers.get('status', None) == 404
    assert sender.body() == ''


async def test_module_doesnt_exist(patch_app):  # type: ignore
    """
    If the requested Python module doesnt exist, the app will respond
    with a 404.
    """
    patch_app('basic')
    sender = await asgi_get('/_blu_internal/app_module/foo')
    headers = next(sender)
    assert headers.get('status', None) == 404
    assert sender.body() == ''


async def test_reject_single_dot_segment(patch_app):  # type: ignore
    """Rejects module paths with the segment '.'."""
    patch_app('app_module_reject')


async def test_reject_double_dot_segment(patch_app):  # type: ignore
    """Rejects module paths with the segment '..'."""
    patch_app('app_module_reject')


async def test_reject_stars_in_segments(patch_app):  # type: ignore
    """Rejects module paths that include an asterisk."""
    patch_app('app_module_reject')


async def test_reject_pycache_dir(patch_app):  # type: ignore
    """Rejects module paths with the segment '__pycache__'."""
    patch_app('app_module_reject')