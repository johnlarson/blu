from collections import defaultdict
import urllib.parse

from blu._nodes import Node
from blu._utils.typing import Iterator, Mapping

type QueryInit = Mapping[str, str | list[str]]


class QueryParams:
    """
    The query parameters in a request URL.

    .. code-block:: python

        from blu import Request

        request = Request('GET', '/?my-query-param=my-value')

        request.query().get('my-query-param') == 'my-value'
    """

    _items: dict[str, list[str]]

    @classmethod
    def from_query_string(cls, query_string: str) -> "QueryParams":
        """
        Parse a query string.

        :param query_string: The query string to parse, without the
            leading ``?`` character.

        :return: The :class:`QueryParams` representation of the query
            string.
        """
        pair_strings = query_string.split("&") if query_string else []
        pairs = [x.split("=") for x in pair_strings]
        query_params_init: dict[str, list[str]] = defaultdict(lambda: [])
        for k, v in pairs:
            decoded = urllib.parse.unquote_plus(v)
            query_params_init[k].append(decoded)
        return QueryParams({**query_params_init})

    def __init__(self, items: QueryInit):
        """
        .. code-block:: python

            # ?sortBy='relevance&q=position&q=velocity&q=acceleration
            QueryParams({
                'sortBy': 'relevance',
                'q': ['position', 'velocity', 'acceleration'],
            })
        :param items: A mapping of query parameter names to values. If
            a query parameter has only one value, then its value can be
            represented as a :py:class:`str`. If it has more than one
            value, it should be represented as a
            :py:class:`list` of :py:class:`str`\\ s.
        """
        self._items = {k: v if isinstance(v, list) else [v] for k, v in items.items()}

    def __getitem__(self, key: str) -> str:
        """
        Get the value of a query parameter.

        .. code-block:: python

            QueryParams.from_query_string('x=value')['x'] == 'value'

        :param key: A query parameter name.

        :return: The value of that query parameter. If the parameter has
            multiple values (e.g. ``a=1&1=34``), returns the first.

        :raise KeyError: If the :class:`QueryParams` object has no
            query parameter with the name specified by :data:`key`.
        """
        return self._items[key][0]

    def get[T](self, key: str, default: T = None) -> str | T:
        """
        Get the value of a query parameter.

        .. code-block:: python

            QueryParams.from_query_string('a=1').get('a') == '1'

        :param key: The name of a query parameter.
        :param default: A default value.

        :return: The value of the query parameter named **key** if it
            exists. Otherwise, **default**. If there are multiple values
            associated with **key**, returns the first.
        """
        try:
            return self._items[key][0]
        except KeyError:
            return default

    def all(self, key: str) -> list[str]:
        """
        Get all values associated with a query parameter key.

        .. code-block:: python

            q = QueryParams.from_query_string('a=1&a=2')
            q.all('a') == ['1', '2']

        :param key: A query parameter key.

        :return: A :py:class:`list` of all values associated with the
            given query parameter key, in the order they appear in the
            query string, or, if the :class:`QueryParams` object was
            not created from a query string, the order they were defined
            in the data passed into the :class:`QueryParams`
            constructor.
        """
        return self._items.get(key, [])

    def __iter__(self) -> Iterator[tuple[str, list[str]]]:
        """
        Iterate over the keys and value lists of ``self``.

        .. code-block:: python

            q = QueryParams.from_query_string('a=1&b=2&b=3')
            for name, values in q:
                print(f'{name}:', ', '.join(values))

        .. code-block:: console

            a: 1
            b: 2, 3

        :return: An iterator of key-value pairs, where the key is a
            query parameter name, and the value is a list of all string
            values associated with that name in the query string. Pairs
            occur in the order of names' first appearance in the query
            string, and query values within a pair are in the order in
            which they are set in the query string.
        """
        return ((k, v) for k, v in self._items.items())

    def to_query_string(self) -> str:
        """
        Serialize ``self`` to a query string.

        .. code-block:: python

            q = QueryParams.from_query_string('a=1&b=2')
            q.to_query_string() == 'a=1&b=2'

        :return: The query string representation of the query parameters
            in ``self``.
        """
        pairs: list[str] = []
        for k, vals in self:
            for v in vals:
                pairs.append(f"{k}={v}")
        return "&".join(pairs)


class Request:
    method: str
    path: str
    query: QueryParams
    headers: dict[str, str]

    def __init__(
        self,
        path: str,
        query: QueryParams | QueryInit = QueryParams({}),
        headers: Mapping[str, str] = {},
    ):
        self.path = path
        if isinstance(query, QueryParams):
            self.query = query
        else:
            self.query = QueryParams(query)
        self.headers = {**headers}


class Response:
    """
    An HTTP response for a page in a web application. Return a
    :class:`Response <blu.Response>` from a ``__page__`` function (see
    :ref:`api-reference/file-conventions:File Conventions`) to set HTTP
    status and headers for that page.

    .. code-block:: python
        :caption: __index__.py

        def __page__():
            return Response(
                p['Hello.'],
                status=404,
                headers={
                    'Cache-Control': 'no-cache',
                    'Last-Modified': 'Tue, 10 Dec 2024 10:00:00 GMT',
                },
            )

    :param body: The React node to render when displaying the page.
    :param status: The status code to send in the HTTP response.
    :param headers: The HTTP headers to send in the HTTP response.
    """

    _body: Node
    _status: int
    _headers: dict[str, str]

    def __init__(
        self,
        body: Node = None,
        status: int = 200,
        headers: Mapping[str, str] = {},
    ):
        self._body = body
        self._status = status
        self._headers = {**headers}
