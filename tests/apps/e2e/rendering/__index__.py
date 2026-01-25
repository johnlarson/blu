from blu import Key
from blu.html import del_, span

__client__ = True


def __page__():
    return del_(id='my-id')[
        span['A'],
        'B',
        ('C', 'D'),
        ['IN LIST'],
        # Key(1)['FRAGMENT'],
        #[Key(1)['E'], Key(2)['F']],
        1,
        2.0,
        None,
        True,
        False,
    ]