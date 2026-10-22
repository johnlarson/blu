Sessions
========

You can store data across requests for a given user using ``session``:

.. code-block:: python

    from blu import session


    def __page__():
        session['a'] = 1
        return 'Hello'

Session keys must be ``str``\ s, and values must be JSON-serializable.

.. warning::

   Do not include any sensitive data in the session, as it can be read by the client.

In order to use sessions, ``__settings__.py`` must have a ``SECRET_KEY`` setting:

.. code-block:: python
    :caption: app/__settings__.py

    SECRET_KEY = '...'

.. warning::

   Keep this key secret. Do not include it in version control. Anyone with this key has the ability to forge session data.
