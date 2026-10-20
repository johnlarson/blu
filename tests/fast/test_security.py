from pathlib import Path
from typing import cast
from zipfile import ZipFile

import aiohttp
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
    # If another site attempts send a request using fetch, it won't succeed.

    httpserver.expect_request("/").respond_with_data("Other Site")
    p = await page("server_function_csrf")
    from app.server_functions import value

    host_and_port = cast(str, p.base_url).replace("http://", "")
    host, port_str = host_and_port.split(":")
    port = int(port_str)
    await p.goto(httpserver.url_for("/"))

    async def fetch_fn(value: int) -> tuple[int, str]:
        return await p.evaluate(
            f"""
                async () => {{
                    const response = await fetch(
                        '{p.base_url}/_blu_internal/server_function',
                        {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{
                                module: 'app.server_functions',
                                name: 'change_value',
                                args: [{value}],
                                kwargs: {{}},
                            }}),
                        }},
                    );
                    return response.status;
                }}
            """
        )

    try:
        await fetch_fn("SET BY CROSS-SITE FETCH")
    except Exception as e:
        assert "TypeError: Failed to fetch" in str(e)
    else:
        assert False  # If didn't raise error, fail.
    assert value[0] == "UNTOUCHED"

    p.goto("/")
    status = await fetch_fn("SET BY SAME ORIGIN")
    assert status == 200
    assert value[0] == "SET BY SAME ORIGIN"

    # If Blu receives a request without the header Content-Type:
    # application/json, it won't accept it.
    async with aiohttp.ClientSession(p.base_url) as session:

        # Without Content-Type header
        response = await session.post(
            f"{p.base_url}/_blu_internal/server_function",
            json={
                "module": "app.server_functions",
                "name": "change_file_contents",
                "args": ["SET WITH NO CONTENT-TYPE"],
                "kwargs": {},
            },
        )
        assert response.status == 415
        assert await response.text() == ""
        assert value[0] == "SET BY SAME ORIGIN"

        # Wrong Content-Type
        response = await session.post(
            f"{p.base_url}/_blu_internal/server_function",
            headers={"Content-Type": "text/javascript"},
            json={
                "module": "app.server_functions",
                "name": "change_file_contents",
                "args": ["SET WITH WRONG CONTENT-TYPE"],
                "kwargs": {},
            },
        )
        assert response.status == 415
        assert await response.text() == ""
        assert value[0] == "SET BY SAME ORIGIN"

        # With Content-Type: application/json
        response = await session.post(
            f"{p.base_url}/_blu_internal/server_function",
            headers={"Content-Type": "application/json"},
            json={
                "module": "app.server_functions",
                "name": "change_file_contents",
                "args": ["SET WITH CONTENT-TYPE APPLICATION/JSON"],
                "kwargs": {},
            },
        )
        assert response.status == 200
        assert value[0] == "SET WITH CONTENT-TYPE APPLICATION/JSON"

    # If Blu receives an non-POST request, it will respond with a 405.
    async with aiohttp.ClientSession(p.base_url) as session:

        def test_method(method: str, body: bool = True) -> tuple[int, str]:
            extra_kwargs = (
                {
                    "json": {
                        "module": "app.server_functions",
                        "name": "change_file_contents",
                        "args": [method],
                        "kwargs": {},
                    },
                }
                if body
                else {}
            )
            response = await session.post(
                f"{p.base_url}/_blu_internal/server_function",
                headers={"Content-Type": "application/json"},
                **extra_kwargs,
            )
            return (response.status, await response.text())

        assert test_method("POST")[0] == 200
        assert value[0] == "POST"
        assert test_method("GET", body=False) == (405, "")
        assert value[0] == "POST"
        assert test_method("HEAD", body=False) == (405, "")
        assert value[0] == "POST"
        assert test_method("OPTIONS") == (405, "")
        assert value[0] == "POST"
        assert test_method("PUT") == (405, "")
        assert value[0] == "POST"
        assert test_method("PATCH") == (405, "")
        assert value[0] == "POST"
        assert test_method("DELETE") == (405, "")
        assert value[0] == "POST"
        assert test_method("MADEUPMETHOD") == (405, "")
        assert value[0] == "POST"


async def test_server_function_no_call_arbitrary_function(
    client: ClientFixture,
):
    """
    If a function is not marked as a server function, it cannot be
    called client-side.
    """
    c = await client("server_function_arbitrary_function_call")

    from app.server_functions import callable_called, non_callable_called
    from app.server_only_module import server_only_function_called

    origin = str(c._base_url_origin)

    # Sanity check -- this should succeed.
    r = await c.post(
        "/_blu_internal/server_function",
        headers={"Origin": origin},
        json={
            "module": "app.server_functions",
            "name": "callable",
            "args": [350],
            "kwargs": {},
        },
    )
    assert r.status == 200
    assert callable_called == [True]

    # Non-server function in same module as server function
    r = await c.post(
        "/_blu_internal/server_function",
        headers={"Origin": origin},
        json={
            "module": "app.server_functions",
            "name": "should_not_be_callable",
            "args": [],
            "kwargs": {},
        },
    )
    assert r.status == 404
    data = await r.json()
    assert data["error"] == "Not Found"
    assert non_callable_called == [False]

    # Non-server function in module with no server functions
    r = await c.post(
        "/_blu_internal/server_function",
        headers={"Origin": origin},
        json={
            "module": "app.server_only_module",
            "name": "server_only_function",
            "args": [],
            "kwargs": {},
        },
    )
    assert r.status == 404
    data = await r.json()
    assert data["error"] == "Not Found"
    assert server_only_function_called == [False]

    # Standard library function
    r = await c.post(
        "/_blu_internal/server_function",
        headers={"Origin": origin},
        json={
            "module": "platform",
            "name": "system",
            "args": [],
            "kwargs": {},
        },
    )
    assert r.status == 404
    data = await r.json()
    assert data["error"] == "Not Found"
    assert server_only_function_called == [False]


async def test_server_functions_cannot_be_called_outside_app_package(
    client: ClientFixture,
):
    """
    Even if it is decorated with the @blu.server decorator, a function
    cannot be called from the client if it is not in the app package.
    """
    c = await client("server_functions_outside_app")
    origin = str(c._base_url_origin)

    # Sanity check; this should succeed.
    await c.post(
        "/_blu_internal/server_function",
        headers={"Origin": origin},
        json={
            "module": "app.valid",
            "name": "valid",
            "args": [],
            "kwargs": {},
        },
    )
    from app.valid import valid_called

    assert valid_called == [True]

    # This should fail.
    r = await c.post(
        "/_blu_internal/server_function",
        headers={"Origin": origin},
        json={
            "module": "tests.resources.invalid",
            "name": "invalid",
            "args": [],
            "kwargs": {},
        },
    )
    assert r.status == 404
    from tests.resources.server_fn_outside_app import invalid_called

    assert invalid_called == [False]
