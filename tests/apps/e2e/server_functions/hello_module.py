from blu import server

from app.shared import A


@server
def hello(value):
    return A(value)
