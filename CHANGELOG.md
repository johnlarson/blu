# Changelog

## Unreleased

### Security

- Update server function CSRF protection to use the "Avoiding simple requests" defense described in https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/CSRF#avoiding_simple_requests.

### Added

- Add support for HTTP proxying.
- Add secure session support.

## v0.0.3 - 2026-10-12

_Blu now uses MicroPython by default and no longer uses PyScript. If you are upgrading from v0.0.2, add `INTERPRETER = 'pyodide'` to your `__settings__.py` and remove any references to the `pyscript`._

### Added

- Add support for MicroPython in client-side code.

### Changed

- **Breaking** Use `*` instead of `/` to separate route parameters and query parameters in route handlers.
- **Breaking** Make MicroPython the default client-side Python interpreter (use previous default interpreter by adding `INTERPRETER = 'pyodide'` to `__settings__.py`).

### Removed

- **Breaking** Remove support for async callbacks in `blu.use_effect()`.