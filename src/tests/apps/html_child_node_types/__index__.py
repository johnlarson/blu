from blu.html import div, span, p


def __page__():
    return div(className='my-div')[
        span,
        'Hello!',
        None,
        True,
        False,
        1,
        1.0,
        (
            p,
            'Hello again!',
            None,
            True,
            False,
            2,
            2.0,
        )
    ]