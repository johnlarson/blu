from blu.html import b, p


def __page__(*, bar, baz):
    return (
        p(className='bar')[
            b['bar:'], ' ', bar,
        ],
        p(className='baz')[
            b['baz:'], ' ', baz,
        ],
    )