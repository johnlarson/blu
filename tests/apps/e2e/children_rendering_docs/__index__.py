from blu import client
from blu.html import span

__client__ = True


def __page__():
    return ColoredText("red")["This should be red.",]


@client
def ColoredText(color):
    return span(style={"color": color})[(yield),]
