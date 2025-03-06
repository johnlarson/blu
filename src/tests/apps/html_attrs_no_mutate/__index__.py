from blu.html import body, div, html


def __page__():
    without_attributes = div(id='without-attributes')
    with_attributes = div(id='with-attributes', a='1', b='2')
    return html[
        body[
            without_attributes,
            with_attributes,
        ]
    ]