def test_dev_server():
    """
    When a `blu dev` is run, a dev server starts up that serves the app
    on a port that is given by the output to `blu dev`.
    """
    ...


def test_static():
    """The dev server serves static files."""
    ...


def test_server_only_modules():
    """
    The dev server does not serve Python modules statically for which
    module.__client__ == False.
    """
    ...


def test_client_modules():
    """
    The dev server serves Python modules statically for which
    module.__client__ == True.
    """
    ...