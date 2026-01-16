from blu.html import b, p


def __page__(foo, *, bar, baz):
    return (
        p(className='foo')[
            b['foo:'], ' ', foo,
        ],
        p(className='bar')[
            b['bar:'], ' ', bar,
        ],
        p(className='baz')[
            b['baz:'], ' ', baz,
        ],
    )