from blu import is_client
from blu.html import div


def __page__():
    return div(id='is_client')[is_client]