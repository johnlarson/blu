def test_client_modules():
    """
    Any python module under the app package for which
    module.__client__ == True will be available client-side.
    """
    ...


def test_no_client_marker():
    """
    Any python module under the app package for which module.__client__
    is not set will be unavailable client-side.
    """
    ...


def test_client_not_true():
    """
    Any python module under the app package for which module.__client__
    is not True will be unavailable client-side.
    """
    ...


def test_non_app_packages():
    """
    Modules outside the app package are unavailable client-side,
    regardless of the value of module.__client__.
    """
    ...