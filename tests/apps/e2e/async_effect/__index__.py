from blu import client, use_effect
from blu._hooks import use_state
from blu.html import button, div


__client__ = True


def __page__():
    return MyClientElement


@client
def MyClientElement():
    from js import alert

    render_num, set_render_num = use_state(1)
    events = use_ref([])

    @use_effect
    async def _():
        events[:] = [*events, "SETUP"]
        yield
        events[:] = [*events, "TEARDOWN"]

    @use_effect
    async def _():
        events[:] = [*events, "SETUP ONLY"]

    def handle_click(e):
        set_render_num(render_num + 1)

    return div[button(onClick=handle_click), div(id="events")[",".join(events[:])]]
