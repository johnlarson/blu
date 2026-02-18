import uuid
from blu import HTMLElement, Ref, client, use_effect, use_ref, use_state
from blu.html import button, div

__client__ = True


def __page__():
    return RefTest


@client
def RefTest():
    div_ref = use_ref()

    @use_effect
    def _():
        div_ref[:].innerText = "Hello."

    return div(id="test-div", ref=div_ref)
