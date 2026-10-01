from blu import client
from blu.html import div, p

__client__ = True


def __page__():
    return MyClientElement


@client
def MyClientElement():
    import arrr
    import emoji

    return div[
        p[arrr.translate("Hello there.")],
        p[emoji.emojize(":thumbs_up:")],
    ]
