from blu import client
from blu.html import html, head, body, button



def __page__():
    return html[
        head,
        body[
            HelloButton,
        ],
    ]


@client
def HelloButton():
    return button(onClick=say_hello)['Click me!']


def say_hello(e):  # type: ignore
    from js import alert  # type: ignore
    print('Clicked!')
    alert('Hello!')