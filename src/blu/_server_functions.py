from typing import Any
from collections.abc import Awaitable, Callable

from blu._utils.client import is_client
from blu._utils import json


def server[
    **P, R
](callable: Callable[P, R | Awaitable[R]],) -> Callable[P, Awaitable[R]]:
    """
    .. danger::

        Don't use this in production. The only exception to this rule is
        when:

        1. The server function doesn't change any persistent state (no
        writing files, updating databases, etc.), *AND*

        2. The server function does not return any sensitive data.

        The :func:`@server <blu.server>` function security strategy is
        still being planned and has not been implemented.

    Create a server function that can be called from the client.

    .. code-block:: python
        :caption: app/server_functions.py

        from blu import server


        @server
        def read_greeting_from_file(name):
            with open('app/hello.txt', 'r') as f:
                return f.read() + name

    .. code-block:: none
        :caption: app/hello.txt

        Hello,

    .. code-block:: python
        :caption: app/__index__.py

        from blu import client
        from blu.html import div

        __client__ = True


        def __page__():
            return MyClientElement


        @client
        def MyClientElement():
            return div[read_greeting_from_file('George')]

    .. code-block:: html

        <div>Hello, George!</div>

    :param callable: A :class:`Callable <collections.abc.Callable>`
    :return: An asynchronous function that, when called in a client
        environment, runs ``callable`` on the server with the provided
        arguments, and returns the return value of ``callable``.

    When calling the returned function in a client environment, the
    arguments provided must be JSON-serializable and the return value
    must be picklable. Otherwise, the function will be unable to
    complete.

    The function must be defined at the top level of a module in order
    to be accessible client-side.

    .. code-block:: python
        :caption: Wrong!

        class A:

            @server
            def func():
                return 1


    .. code-block:: python
        :caption: Wrong!

        def func_factory():

            @server
            def func():
                return 1

            return func

    .. code-block:: python
        :caption: Right.

        @server
        def func():
            return 1
    """

    # if is_client:
    #     from pyscript import fetch
    #     async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Awaitable[R]:
    #         url = (
    #             f'/_blu_interna/server_functions/{fn.__module__}/{fn.__name__}'
    #         )
    #         response = await fetch(
    #             url,
    #             method='POST',
    #             body=await json.dumps({
    #                 'args': args,
    #                 'kwargs': kwargs,
    #             }),
    #             headers={
    #                 'Content-Type': 'application/json',
    #             },
    #         )
    # elif isinstance(fn, Awaitable):
    #     return fn
    # else:
    #     return asyncify(fn)
    ...
