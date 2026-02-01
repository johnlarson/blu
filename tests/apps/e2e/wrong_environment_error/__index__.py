from blu import Response, WrongEnvironmentError, app, client
from blu.html import div

__client__ = True


def __page__():
    return Foo


@client
def Foo():
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