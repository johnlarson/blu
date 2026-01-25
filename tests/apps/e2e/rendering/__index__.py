import copyreg
from blu import Key, client
from blu.html import del_, span

__client__ = True


def __page__():
    return del_(id='my-id')[
        Simple,
        span['A'],
        'B',
        ('C', 'D'),
        [Key(1)['E'], Key(2)['F']],
        1,
        2.0,
        None,
        True,
        False,
        DoubleRender('Y')[span['Z']]
    ]


@client
def Simple():
    return 'Hello, World!'


@client
def DoubleRender(a):
    return Complex(a)[(yield)]


@client
def Complex(a):
    return span[a, span[(yield)]]
