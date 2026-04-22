

# Blu

*Blu is still in early testing and should not be used in production applications.*

A full stack React framework for Python.


```python
from blu import client
from blu.html import html, head, body, h1, button

__client__ = True


def __page__():
    return html[
        head,
        body[
            h1[
                ClickCounter
            ]
        ]
    ]
    return ClickCounter


@client
def ClickCounter():
    count, set_count = use_state(0)

    def handle_click(e):
        set_count(count + 1)
    
    return button(onClick=handle_click)[f"Clicks: {count}"]
```

## Installation

```bash
pip install -U blu-react
```

## Documentation

Documentation available on  [readthedocs.io](<https://blu-react.readthedocs.io>)