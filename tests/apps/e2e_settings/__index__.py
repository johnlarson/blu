from blu import client
from blu.html import div, p

__client__ = True


def __page__():
    return MyClientElement


@client
def MyClientElement():
    import abc
    import io

    return div[
        p[abc.ABC.__name__],
        p[io.SEEK_SET],
    ]
