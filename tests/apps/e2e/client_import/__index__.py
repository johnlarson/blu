from blu import client
from blu.html import div

__client__ = True


def __page__():
    return Foo


@client
def Foo():
    from js import window
    from pyscript.ffi import create_proxy

    return div(id="status")["Success!"]
