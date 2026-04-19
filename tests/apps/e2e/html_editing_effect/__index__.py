from blu import client, use_effect, use_ref
from blu.html import div

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
