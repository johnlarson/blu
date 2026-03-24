from pathlib import Path
from zipfile import ZipFile


def test_server_functions_no_expose_server_only_modules(patch_app, tmp_path: Path):
    """
    Modules that are not marked ``__client__ = True`` are not shipped to the
    client as full source. If they only expose :func:`blu.server` callables at
    module scope, a minimal stub (``@server`` plus signature and ``...`` body)
    is included in ``app_pkg.zip`` under the same import path instead.
    """
    patch_app("e2e")
    from blu._app import _app_pkg_zip

    _app_pkg_zip(tmp_path)
    with ZipFile(tmp_path / "app.zip") as zf:
        data = zf.read("server_functions/hello_module.py").decode()

        assert "def hello(" in data
        assert "@server" in data
        assert "..." in data
        assert "A(" not in data
        assert "from app.server_functions.shared" not in data
        assert "return " not in data
