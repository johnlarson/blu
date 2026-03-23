def test_server_functions_no_expose_server_only_modules():
    """
    Marking a function as a server function does not cause the file to
    be accessible to the outside world; it still needs
    "__client__ = True" in order for it to be available client-side.

    TODO: implement this
    """
