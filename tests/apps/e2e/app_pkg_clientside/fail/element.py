from blu import client
from blu.html import div

__client__ = True


@client
def Foo():
    try:
        from app.app_pkg_clientside.fail.module import A

        return div(id="status")[A]
    except ImportError:
        return div(id="status")["Fail."]
