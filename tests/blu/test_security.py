from asyncio import sleep
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from pytest_httpserver import HTTPServer

from tests.utils import ClientFixture, PageFixture


async def test_server_functions_no_expose_server_only_modules(
    client: ClientFixture, tmp_path: Path
):
    """
    Modules that are not marked ``__client__ = True`` are not shipped to the
    client as full source. If they only expose :func:`blu.server` callables at
    module scope, a minimal stub (``@server`` plus signature and ``...`` body)
    is included in ``app_pkg.zip`` under the same import path instead.
    """
    c = await client("e2e")
    response = await c.get("/_blu_internal/app_pkg.zip")
    zip_path = tmp_path / "app_pkg.zip"
    with open(zip_path, "wb") as zip_f_write:
        async for chunk in response.content.iter_chunked(1024):
            zip_f_write.write(chunk)
    with ZipFile(zip_path, "r") as zip_f_read:
        zip_f_read.extractall(tmp_path)
    with open(tmp_path / "server_functions/hello_module.py", "r") as f:
        data = f.read()
    assert "def hello(" in data
    assert "@server" in data
    assert "..." in data
    assert "A(" not in data
    assert "from app.server_functions.shared" not in data
    assert "return " not in data


async def test_no_access_non_client_files(client: ClientFixture, tmp_path: Path):
    """
    Python files within the app package are not accessible from outside
    the server unless they contain the top-level statement
    "__client__ = True".
    """
    c = await client("e2e")
    response = await c.get("/_blu_internal/app_pkg.zip")
    zip_path = tmp_path / "app_pkg.zip"
    with open(zip_path, "wb") as zip_f_write:
        async for chunk in response.content.iter_chunked(1024):
            zip_f_write.write(chunk)
    with ZipFile(zip_path, "r") as zip_f_read:
        zip_f_read.extractall(tmp_path)
    success_path = tmp_path / "app_pkg_clientside/success/module.py"
    assert success_path.exists()
    fail_path = tmp_path / "app_pkg_clientside/fail/module.py"
    assert not fail_path.exists()


async def test_server_function_csrf(page: PageFixture, httpserver: HTTPServer):
    """
    Server functions can only be called from a page served by the
    associated Blu application, will not be called from requests that
    have any method other than POST.
    """
    httpserver.expect_request("/").respond_with_data("Other Site")
    p = await page("server_function_csrf")
    await p.goto(httpserver.url_for("/"))

    async def fetch_fn(method: str):
        await p.evaluate(
            f"""
                async () => (
                    await fetch(
                        '{p.base_url}/_blu_internal/server_function',
                        {{
                            method: '{method}',
                            body: JSON.stringify({{
                                module: 'app.server_functions',
                                name: 'change_file_contents',
                                args: [],
                                kwargs: {{}},
                            }}),
                        }},
                    )
                )
            """
        )

    try:
        await fetch_fn("POST")
    except Exception as e:
        assert "TypeError: Failed to fetch" in str(e)
    else:
        assert False  # If didn't raise error, fail.

    async def assert_405(method: str):
        try:
            await fetch_fn(method)
        except Exception as e:
            a = 1
        else:
            assert False

    await p.goto("/")
    await assert_405("GET")
    await assert_405("HEAD")
    await assert_405("OPTIONS")
    await assert_405("PUT")
    await assert_405("PATCH")
    await assert_405("DELETE")
    await assert_405("MADEUPMETHOD")

    # TODO specifically test to ensure the server function call is
    # blocked when origin header doesn't match "Host" header.

    from app.server_functions import value

    assert value[0] == "UNTOUCHED"
