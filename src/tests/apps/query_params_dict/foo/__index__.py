from blu.html import b, p


def __page__(*, bar, **kwargs):
    return (
        p(className='bar')[
            b['bar:'], ' ', bar,
        ],
        p(className='baz')[
            b['baz:'], ' ', kwargs['baz'],
        ],
        p(className='hello')[
            b['hello:'], ' ', kwargs['hello']
        ],
    )