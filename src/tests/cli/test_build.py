def test_copies_static_files():
    """
    When `blu build` is run from the command line in the project root
    directory (the parent of the app directory), all non-python files
    are copied over to <root directory>/static, following the same
    directory structure that they had under <root directory>/app.
    """
    ...