from pathlib import Path

import pytest
from tests.utils import asgi_get


async def test_blu_available_client_side(patch_app):  # type: ignore
    """A Blu app should serve Blu root module file."""
    patch_app('basic')
    sender = await asgi_get('/_blu_internal/blu_module')
    repo_root = Path(__file__).parent.parent.parent
    file_path = repo_root / 'src/blu/__init__.py'
    expected = file_path.read_text()
    assert sender.body() == expected


async def test_blu_submodule_available_client_side(patch_app):  # type: ignore
    """A Blu app should serve submodules of the Blu package."""
    patch_app('basic')
    sender = await asgi_get('/_blu_internal/blu_module/html')
    repo_root = Path(__file__).parent.parent.parent
    file_path = repo_root / 'src/blu/html.py'
    expected = file_path.read_text()
    assert sender.body() == expected


async def test_reject_double_dot_segment(patch_app):  # type: ignore
    """Rejects module paths with the segment '..'."""
    patch_app('basic')
    with pytest.raises(AssertionError):
        await asgi_get('/_blu_internal/blu_module/../html')


async def test_reject_stars_in_segments(patch_app):  # type: ignore
    """Rejects module paths that include an asterisk."""
    patch_app('basic')
    with pytest.raises(AssertionError):
        await asgi_get('/_blu_internal/blu_module/*')


async def test_reject_pycache_dir(patch_app):  # type: ignore
    """Rejects module paths with the segment '__pycache__'."""
    patch_app('basic')
    with pytest.raises(AssertionError):
        await asgi_get('/_blu_internal/blu_module/__pycache__/module.py')