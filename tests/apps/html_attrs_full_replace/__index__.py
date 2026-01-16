from blu.html import body, div, html


def __page__():
    original = div(a='1', b='2')
    return html[
        body[
            original(c='3', d='4'),
        ],
    ]