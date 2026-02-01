from blu import Response, WrongEnvironmentError, app
from blu.html import div


def __page__():
    errors: list[str] = []
    try:
        app(None, None, None)
    except WrongEnvironmentError:
        errors.append('app')
    try:
        Response()
    except WrongEnvironmentError:
        errors.append('Response')

    return div(id='errors')[','.join(errors)]