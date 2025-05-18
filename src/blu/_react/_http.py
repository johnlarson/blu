from types import EllipsisType
from blu._utils.typing import Any, Mapping, Optional
from blu._context import (
    DependencyMapContext, DependencyMapJSONContext, ImportMapContext
)
from blu._http import Response
from blu._react._render import Renderer
from blu._react.types import Node


class ReactResponse(Response):
    """
    A :class:`Response` whose body is generated from a :type:`Node`.

    .. code-block:: python

        from blu.html import h1

        ReactResponse(
            h1['404 Not Found'],
            status=404,
        )
    """

    _root_node: Node

    def __init__(
        self,
        body: Node = None,
        status: int | EllipsisType = ...,
        headers: Optional[Mapping[str, str]] | EllipsisType = ...,
        context: Optional[dict[Any, Any]] | EllipsisType = ...,
        base: Optional[Response] = None,
    ):
        """
        :param method: (see :func:`Request`)
        :param path: (see :func:`Request`)
        :param body: The :type:`Node` from which the response body
            should be generated.
        :param headers: (see :func:`Request`)
        :param http_version: (see :func:`Request`)
        :param query: (see :func:`Request`)
        :param params: (see :func:`Request`)
        :param context: (see :func:`Request`)
        :param base: (see :func:`Request`)
        """
        super().__init__('', status, headers, context, base)
        self.headers = {
            'Content-Type': 'text/html',
            **self.headers
        }
        self._root_node = body

    def react(self) -> Node:
        """
        Get the response body's underlying React node.

        .. code-block:: python

            response_body = div['Hello World!']
            ReactResponse(response_body).react() == response_body
        
        :return: The underlying :type:`Node` that the response body will be
            rendered from.
        """
        return self._root_node
    
    async def get_body(self) -> str:
        return await self._get_renderer().render_to_str(self._root_node)

    def _get_renderer(self) -> Renderer:
        return Renderer(
            react_location='https://esm.sh/react@18.3.1',
            react_dom_location='https://esm.sh/react-dom@18.3.1',
            dependency_map=DependencyMapContext.get(None),
            dependency_map_json=DependencyMapJSONContext.get(None),
            importmap=ImportMapContext.get(None),
        )

    def copy(
        self,
        status: int | EllipsisType = ...,
        headers: Optional[Mapping[str, str]] | EllipsisType = ...,
        context: Optional[dict[Any, Any]] | EllipsisType = ...,
    ) -> 'ReactResponse':
        """
        Create a copy of :data:`self`, with the given changes.

        .. code-block:: python

            response.copy(method='POST')

        :param method: (see :meth:`Request.copy`)
        :param path: (see :meth:`Request.copy`)
        :param headers: (see :meth:`Request.copy`)
        :param http_version: (see :meth:`Request.copy`)
        :param query: (see :meth:`Request.copy`)
        :param params: (see :meth:`Request.copy`)
        :param context: (see :meth:`Request.copy`)

        :return: A :class:`ReactResponse` instantiated with :data:`self`
            passed in as the :data:`base` argument, and all other
            arguments taken from the call to :meth:`ReactResponse.copy`
        """
        return ReactResponse(
            status=status,
            headers=headers,
            context=context,
            base=self,
        )