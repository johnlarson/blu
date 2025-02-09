from blu.html import (
    html, head, body, div, span, select, canvas, mymadeuptagname
)

def __page__():
    return html[
        head,
        body[
            div,
            span,
            select,
            canvas,
            mymadeuptagname,
        ],
    ]