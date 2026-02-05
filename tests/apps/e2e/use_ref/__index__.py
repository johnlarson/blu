import uuid
from blu import HTMLElement, Ref, client, use_effect, use_ref, use_state
from blu.html import button, div

__client__ = True


def __page__():
    return RefTest


@client
def RefTest():
    render_id, rerender = use_state(0)
    count_ref = use_ref(0)

    def click_increment(e):
        count_ref[:] = count_ref[:] + 1

    def click_rerender(e):
        rerender(render_id + 1)

    return (
        div(id="count")[count_ref[:]],
        button(id="increment", onClick=click_increment)["Increment"],
        button(id="rerender", onClick=click_rerender)["Rerender"],
    )
