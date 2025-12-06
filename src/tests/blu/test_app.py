def test_runs_blu_from_app_module():
    """
    app is an ASGI app that runs the Blu application defined in the
    current Python environment's "app" package.
    """
    ...


def test_raises_WrongEnvironmentError_when_called_on_client():
    """
    Calling app client-side results in a blu.WrongEnvironmentError being
    raised.
    """
    ...
