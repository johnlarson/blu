from pathlib import Path
import pytest
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


async def test_reject_double_dot_segment(patch_app):  # type: ignore
    """Rejects module paths with the segment '..'."""
    patch_app('app_module_reject')
    with pytest.raises(AssertionError):
        await asgi_get('/_blu_internal/app_module/../module')


async def test_reject_stars_in_segments(patch_app):  # type: ignore
    """Rejects module paths that include an asterisk."""
    patch_app('app_module_reject')
    with pytest.raises(AssertionError):
        await asgi_get('/_blu_internal/app_module/*')


async def test_reject_pycache_dir(patch_app):  # type: ignore
    """Rejects module paths with the segment '__pycache__'."""
    patch_app('app_module_reject')
    app_root = Path(__file__).parent.parent / 'apps/app_module_reject'
    module_dir = app_root / '__pycache__'
    module_dir.mkdir(exist_ok=True)
    module_file_path = module_dir / 'module.py'
    module_file_path.touch()
    with pytest.raises(AssertionError):
        await asgi_get('/_blu_internal/app_module/__pycache__/module')