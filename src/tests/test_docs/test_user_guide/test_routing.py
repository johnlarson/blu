from playwright.async_api import Page, expect

from tests.utils import prod_cli, prod_server


async def test_file_based_routing(page: Page):
    """
    From docs:

    Blu uses file-based routing. This means that the path that a page is
    served from is based on the file’s location in the app/.

    For example, if you want to serve the page in the Quickstart guide
    from /path/to/page instead of from /, you would move the
    __index__.py file from app/ to app/path/to/page
    """
    async with prod_cli('tests.apps.file_based_routing') as url:
        await page.goto(url + '/path/to/page')
        await expect(page.locator('body')).to_have_text('Hello World!')


async def test_file_based_routing__server(page: Page):
    """
    From docs:

    Blu uses file-based routing. This means that the path that a page is
    served from is based on the file’s location in the app/.

    For example, if you want to serve the page in the Quickstart guide
    from /path/to/page instead of from /, you would move the
    __index__.py file from app/ to app/path/to/page

    (server)
    """
    async with prod_server('tests.apps.file_based_routing') as url:
        await page.goto(url + '/path/to/page')
        await expect(page.locator('body')).to_have_text('Hello World!')


async def test_dynamic_route_segment(page: Page):
    """
    From docs:

    To add a dynamic route segment, create a directory whose name is
    surrounded by single underscores, like the _employee_id_ directory
    in this example
    """
    async with prod_cli('tests.apps.dynamic_route_segment') as url:
        await page.goto(url + f'/employees/cheese')
        await expect(page.locator('p')).to_have_text(
            'This is an employee profile page.'
        )


async def test_dynamic_route_segment__server(page: Page):
    """
    From docs:

    To add a dynamic route segment, create a directory whose name is
    surrounded by single underscores, like the _employee_id_ directory
    in this example

    (server)
    """
    async with prod_server('tests.apps.dynamic_route_segment') as url:
        await page.goto(url + '/employees/cheese')
        await expect(page.locator('p')).to_have_text(
            'This is an employee profile page.'
        )


async def test_route_param(page: Page):
    """
    From docs:

    Dynamic route segments usually aren’t that useful unless there’s
    actual dyanmic content, so let’s use that employee id from the URL
    path in our page
    """
    async with prod_cli('tests.apps.route_param') as url:
        await page.goto(url + '/employees/325832')
        await expect(page.locator('p')).to_have_text(
            'This is the profile page for employee #325832.'
        )
        

async def test_route_param__server(page: Page):
    """
    From docs:

    Dynamic route segments usually aren’t that useful unless there’s
    actual dyanmic content, so let’s use that employee id from the URL
    path in our page

    (server)
    """
    async with prod_server('tests.apps.route_param') as url:
        await page.goto(url + '/employees/325832')
        await expect(page.locator('p')).to_have_text(
            'This is the profile page for employee #325832.'
        )


async def test_multiple_route_params(page: Page):
    """
    From docs:

    A route can have multiple dynamic segments
    """
    async with prod_cli('tests.apps.multiple_route_params') as url:
        await page.goto(url + '/employees/325832/time_card/2024-12-10')
        await expect(page.locator('p')).to_have_text(
            'This is employee #325832\'s time card for 2024-12-10.'
        )


async def test_multiple_route_params__server(page: Page):
    """
    From docs:

    A route can have multiple dynamic segments

    (server)
    """
    async with prod_server('tests.apps.multiple_route_params') as url:
        await page.goto(url + '/employees/325832/time_card/2024-12-10')
        await expect(page.locator('p')).to_have_text(
            'This is employee #325832\'s time card for 2024-12-10.'
        )


async def test_default_handler(page: Page):
    """
    From docs:

    You can add a catch-all handler to a route segment that handles a
    request if the route is matched up to that point but no __index__.py
    file is on a path that exactly matches the URL. You do this by
    creating a __default__.py file with a __page__() function
    """
    async with prod_cli('tests.apps.default_handler') as url:
        await page.goto(url + '/foo/bar')
        await expect(page.locator('p')).to_have_text(
            'This is the page for /foo/bar.'
        )
        default_text = 'This is the default page.'
        await page.goto(url + '/foo')
        await expect(page.locator('p')).to_have_text(default_text)
        await page.goto(url + '/foo/some/other/path')
        await expect(page.locator('p')).to_have_text(default_text)
        await page.goto(url + '/foo/bar/some/other/path')
        await expect(page.locator('p')).to_have_text(default_text)


async def test_default_handler__server(page: Page):
    """
    From docs:

    You can add a catch-all handler to a route segment that handles a
    request if the route is matched up to that point but no __index__.py
    file is on a path that exactly matches the URL. You do this by
    creating a __default__.py file with a __page__() function

    (server)
    """
    async with prod_server('tests.apps.default_handler') as url:
        await page.goto(url + '/foo/bar')
        await expect(page.locator('p')).to_have_text(
            'This is the page for /foo/bar.'
        )
        default_text = 'This is the default page.'
        await page.goto(url + '/foo')
        await expect(page.locator('p')).to_have_text(default_text)
        await page.goto(url + '/foo/some/other/path')
        await expect(page.locator('p')).to_have_text(default_text)
        await page.goto(url + '/foo/bar/some/other/path')
        await expect(page.locator('p')).to_have_text(default_text)


async def test_default_handler_remaining_path(page: Page):
    """
    From docs:

    To read the remaining, unmatched portion of the URL in a default
    handler, you can accept a positional-only argument in the __page__()
    function. This is done by adding a slash to __page__()’s function
    signature
    """
    async with prod_cli('tests.apps.default_handler_remaining_path') as url:
        await page.goto(url + '/foo/a/b/c')
        await expect(page.locator('p')).to_have_text(
            'The remaining path is a/b/c.'
        )


async def test_default_handler_mix_path_and_route_params(page: Page):
    """
    From docs:

    Any dynamic route arguments should come after the slash
    """
    async with prod_cli(
        'tests.apps.default_handler_path_and_route_params'
    ) as url:
        await page.goto(url + '/my-param-value/a/b/c')
        await expect(page.locator('p.my-param')).to_have_text(
            'my_param value: my-param-value'
        )
        await expect(page.locator('p.path')).to_have_text(
            'remaining path: a/b/c'
        )


async def test_query_params(page: Page):
    """
    From docs:

    To access a request’s query parameters in an __index__.py or
    __default__.py handler, add keyword-only arguments to the __page__()
    function. This is done by adding an asterisk to the function
    signature:
    """
    async with prod_cli('tests.apps.query_params') as url:
        await page.goto(url + '/foo?bar=A&baz=B')
        await expect(page.locator('p.bar')).to_have_text('bar: A')
        await expect(page.locator('p.baz')).to_have_text('baz: B')


async def test_query_params_dict(page: Page):
    """
    From docs:

    The __page__() function can also accept a keyword argument dict
    """
    async with prod_cli('tests.apps.query_params_dict') as url:
        await page.goto(url + '/foo?bar=A&baz=B&hello=C')
        await expect(page.locator('p.bar')).to_have_text('bar: A')
        await expect(page.locator('p.baz')).to_have_text('baz: B')
        await expect(page.locator('p.hello')).to_have_text('hello: C')


async def test_route_params_and_query_params(page: Page):
    """
    From docs:

    If there are dynamic route arguments, those should come before the asterisk
    """
    async with prod_cli('tests.apps.route_params_and_query_params') as url:
        await page.goto(url + '/A?bar=B&baz=C')
        await expect(page.locator('p.foo')).to_have_text('foo: A')
        await expect(page.locator('p.bar')).to_have_text('bar: B')
        await expect(page.locator('p.baz')).to_have_text('baz: C')