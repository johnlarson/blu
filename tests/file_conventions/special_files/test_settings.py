from blu._http import Request
from tests.file_conventions._utils import router


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


async def test_CLIENT_REQUIREMENTS_one_requirement():
    """
    If the CLIENT_REQUIREMENTS is a list with one package name, that
    package will be available to client-side code.
    """
    ...


async def test_CLIENT_REQUIRMENTS_multiple_requirements():
    """
    If the CLIENT_REQUIREMENTS is a list with multiple package names,
    those packages will all be available to client-side code.
    """
    ...


async def test_CLIENT_REQUIREMENTS_default():
    """CLIENT_REQUIREMENTS defaults to an empty list."""
    ...