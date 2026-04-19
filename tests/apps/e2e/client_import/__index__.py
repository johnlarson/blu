from blu import client
from blu.html import div

__client__ = True


def __page__():
    return Foo


@client
def Foo():

    return div(id="status")["Success!"]
