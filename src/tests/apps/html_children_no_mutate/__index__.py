from blu.html import div, span

without_children = div
with_children = div['Hello, World!']


def __page__():
    return span[
        without_children,
        with_children,
    ]