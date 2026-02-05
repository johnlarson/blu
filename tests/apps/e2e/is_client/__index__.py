from blu import client, is_client
from blu.html import div

__client__ = True


def __page__():
    return IsClient


@client
def IsClient():
    return div(id="is_client")[is_client]
