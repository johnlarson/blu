from blu import server

from app.server_functions.shared import A


@server
def hello(value):
    return A(value)
