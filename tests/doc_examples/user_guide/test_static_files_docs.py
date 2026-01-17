from aiohttp import ClientSession as Client

from tests.utils import prod_cli, prod_server


async def test_basic_example(client: Client):
    """
    From docs:

    To serve a static file, place it in your app/ directory in the route
    that it should be served from
    """
    async with prod_cli('tests.apps.static_files') as url:
        res = await client.get(url + '/path/to/static/file.txt')
        assert await res.text() == 'Hello, World!'


async def test_basic_example__debug(client: Client):
    """
    From docs:

    To serve a static file, place it in your app/ directory in the route
    that it should be served from

    (debuggable)
    """
    async with prod_server('tests.apps.static_files') as url:
        res = await client.get(url + '/path/to/static/file.txt')
        assert await res.text() == 'Hello, World!'


async def test_dynamic_route_segment(client: Client):
    """
    From docs:

    When a static file is placed under a dynamic route segment, it is
    still served from a static path.
    """
    async with prod_cli('tests.apps.static_file_under_dynamic_segment') as url:
        res1 = await client.get(
            url + '/static_segment/_dynamic_segment_/my_file.txt'
        )
        assert await res1.text() == 'FILE CONTENT'
        res2 = await client.get(
            url + '/static_segment/some-dynamic-segment-value/my_file.txt'
        )
        assert res2.status == 404


async def test_dynamic_route_segment__debug(client: Client):
    """
    From docs:

    When a static file is placed under a dynamic route segment, it is
    still served from a static path.

    (debuggable)
    """
    async with prod_server(
        'tests.apps.static_file_under_dynamic_segment'
    ) as url:
        res1 = await client.get(
            url + '/static_segment/_dynamic_segment_/my_file.txt'
        )
        assert await res1.text() == 'FILE CONTENT'
        res2 = await client.get(
            url + '/static_segment/some-dynamic-segment-value/my_file.txt'
        )
        assert res2.status == 404