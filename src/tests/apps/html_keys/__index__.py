from blu import Key
from blu.html import div

PEOPLE = [  # type: ignore
    {'id': 0, 'name': 'Ana'},
    {'id': 1, 'name': 'Bill'},
    {'id': 2, 'name': 'Charlotte'},
]


def __page__():
    return div[
        div(className='keyed')[
            [
                Key(person["id"])[
                    f'Hello, {person["name"]}!',
                ]
                for person in PEOPLE  # type: ignore
            ],
        ],
        div(className='tuple')[
            (
                'Hello, Ana!',
                'Hello, Bill!',
                'Hello, Charlotte!',
            ),
        ],
        div(className='str')['Hello, Ana! Hello, Bill! Hello, Charlotte!'],
    ]