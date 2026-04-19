class WrongEnvironmentError(Exception):
    """
    Raised when an attempt is made to perform a server-only action on
    the client, or a client-only action on the server.
    """
