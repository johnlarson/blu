from blu.html import html, head, body, button


def __page__():
    return html[
        head,
        body[
            button(onClick=say_hello),  # type: ignore
        ],
    ]


def say_hello(e):
    print('Hello!')