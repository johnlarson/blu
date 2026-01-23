from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import pytest
from blu._http import Request
from tests.file_conventions._utils import router
from blu._settings import settings


@pytest.fixture
def set_settings(monkeypatch: pytest.MonkeyPatch):
    with TemporaryDirectory() as temp_dir:
        def handler(app_name: str):
            to_delete = [
                x for x in sys.modules if x == 'app' or x.startswith('app.')
            ]
            for name in to_delete:
                del sys.modules[name]
            src_path = Path(__file__).parent.parent.parent / 'apps' / app_name
            ln_path = Path(temp_dir) / 'app'
            ln_path.symlink_to(src_path)
            monkeypatch.syspath_prepend(temp_dir)  # type: ignore
            settings.cache_clear()
        yield handler


async def test_no_settings_file():
    """Application runs with no __settings__.py file."""
    r = router('basic')
    response = await r.handle(Request('/'))
    assert response._body == 'Hello, World!'  # type: ignore


async def test_empty_settings_file():
    """Application runs if __settings__.py file is empty."""
    r = router('empty_settings')
    response = await r.handle(Request('/'))
    assert response._body == 'Hello, World!'  # type: ignore


async def test_ignore_settings_file_below_top_level(patch_app):  # type: ignore
    """
    A __settings__.py file below the top level of the app package is
    ignored.
    """
    patch_app('settings_below_top_level')
    assert settings().CLIENT_REQUIREMENTS == []


async def test_CLIENT_REQUIREMENTS_one_requirement(patch_app):  # type: ignore
    """
    If the CLIENT_REQUIREMENTS is a list with one package name, that
    package will be available to client-side code.
    """
    patch_app('settings_one_client_req')
    assert settings().CLIENT_REQUIREMENTS == ['requests']


async def test_CLIENT_REQUIRMENTS_multiple_requirements(patch_app):  # type: ignore
    """
    If the CLIENT_REQUIREMENTS is a list with multiple package names,
    those packages will all be available to client-side code.
    """
    patch_app('settings_multi_client_reqs')
    assert settings().CLIENT_REQUIREMENTS == ['requests', 'flask']


async def test_CLIENT_REQUIREMENTS_default(patch_app):  # type: ignore
    """CLIENT_REQUIREMENTS defaults to an empty list."""
    patch_app('empty_settings')
    assert settings().CLIENT_REQUIREMENTS == []


def test_no_settings_file_use_defaults(patch_app):  # type: ignore
    """
    If no app.__settings__ module, all settings are set to default
    values.
    """
    patch_app('basic')
    s = settings()
    assert s.CLIENT_REQUIREMENTS == []