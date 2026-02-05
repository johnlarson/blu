from blu import client
from blu.html import div
from app.app_pkg_clientside.success.module import A

__client__ = True


@client
def Foo():
    return div(id="status")[A]
