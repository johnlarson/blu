from blu._micropython.typing import Any


class Session:
    """
    Per-user data that persists across requests.

    Access the current request's session via :data:`blu.session`:

    .. code-block:: python

        from blu import session


        def __page__():
            session['a'] = 1
            return 'Hello'

    Keys must be :class:`str`\\ s, and values must be JSON-serializable.

    .. warning::

       Do not include any sensitive data in the session, as it can be
       read by the client.

    In order to use sessions, ``__settings__.py`` must have a
    ``SECRET_KEY`` setting. See
    :ref:`api-reference/file-conventions:__settings__.py`.
    """

    def __getitem__(self, key: str) -> Any:
        """
        Return the value associated with ``key``.

        :param key: A session key.
        :return: The value associated with ``key``.
        :raises KeyError: If ``key`` is not in the session.
        """
        raise NotImplementedError

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Store ``value`` under ``key``.

        :param key: A session key. Must be a :class:`str`.
        :param value: A JSON-serializable value.
        """
        raise NotImplementedError

    def get[T](self, key: str, default: T = None) -> Any | T:
        """
        Return the value for ``key`` if it is in the session, else
        ``default``.

        Like :meth:`dict.get`.

        .. code-block:: python

            session.get('a')  # None if 'a' is not in the session
            session.get('a', 0)  # 0 if 'a' is not in the session

        :param key: A session key.
        :param default: A value to return if ``key`` is not in the
            session. Defaults to ``None``.
        :return: The value associated with ``key``, or ``default`` if
            ``key`` is not in the session.
        """
        raise NotImplementedError


session = Session()
"""The :class:`~blu.Session` for the current request."""
