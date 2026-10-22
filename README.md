

# Blu

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

## Is Blu Right for You?

Read [here](https://blu-react.readthedocs.io/en/latest/appendices/is-blu-right-for-you.html) to ensure Blu meets the needs of your project.

## Documentation

Documentation available at [readthedocs.io](<https://blu-react.readthedocs.io>).