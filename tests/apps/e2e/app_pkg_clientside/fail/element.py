from blu import client
from blu.html import div
from app.app_pkg_clientside.fail.module import A

__client__ = True


@client
def Foo():
    try:
        return div(id='status')[A]
    except ImportError:
        return div(id='status')['Fail.']