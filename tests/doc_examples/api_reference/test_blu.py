from blu import client
from blu.html import b, span
from tests.utils import node_eq, render


def test_ClientElement_example():
    @client
    def ColorfulText(color, bold):
        colorful_span = span(style={'color': color})[(yield)]
        if bold:
            return b[colorful_span]
        else:
            return colorful_span
    
    element = render(
        ColorfulText('red', bold=True)[
            'Danger! The world said hello back.',
        ],
    )

    assert node_eq(
        element,
        b[
            span(style={'color': 'red'})[
                'Danger! The world said hello back.',
            ],
        ],
    )