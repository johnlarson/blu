from tests.utils import asgi_get


async def test_client_modules(patch_app):  # type: ignore
    """
    Any python module under the app package for which
    module.__client__ == True will be available client-side.
    """
    patch_app('client_module')
    body = (await asgi_get('/_blu_internal/app_modules/module')).body()
    assert body == '__client__ = True\n\nA=3'


async def test_no_client_marker(patch_app):  # type: ignore
    """
    Any python module under the app package for which module.__client__
    is not set will be unavailable client-side.
    """
    patch_app('basic')
    sender = await asgi_get('/_blu_internal/app_modules/__index__')
    headers = next(sender)
    assert headers.get('status', None) == 404
    assert sender.body() == 'Not found: /_blu_internal/app_modules/__index__'


async def test_client_not_true(patch_app):  # type: ignore
    """
    Any python module under the app package for which module.__client__
    is not True will be unavailable client-side.
    """
    patch_app('client_false')
    sender = await asgi_get('/_blu_internal/app_modules/module')
    headers = next(sender)
    assert headers.get('status', None) == 404
    assert sender.body() == 'Not found: /_blu_internal/app_modules/module'