from blu.html import b, p


def __page__(path, /, my_param):
    return (
        p(className='my-param')[
            b['my_param value:'], ' ', my_param,
        ],
        p(className='path')[
            b['remaining path:'], ' ', path,
        ],
    )