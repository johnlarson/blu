def test_no_settings_file():
    """Application runs with no __settings__.py file."""
    ...


def test_ignore_settings_file_outside_app_directory():
    """
    A __settings__.py file outside the app package will be ignored.
    """
    ...


def test_ignore_settings_file_below_top_level():
    """
    A __settings__.py file below the top level of the app package is
    ignored.
    """
    ...


def empty_settings_file():
    """Application runs if __settings__.py file is empty."""
    ...


def test_CLIENT_REQUIREMENTS_one_requirement():
    """
    If the CLIENT_REQUIREMENTS is a list with one package name, that
    package will be available to client-side code.
    """
    ...


def test_CLIENT_REQUIRMENTS_multiple_requirements():
    """
    If the CLIENT_REQUIREMENTS is a list with multiple package names,
    those packages will all be available to client-side code.
    """
    ...