from blu import client, use_effect, use_ref, use_state
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
    async def setup_teardown():
        events[:] = [*events, "SETUP"]
        yield
        events[:] = [*events, "TEARDOWN"]

    @use_effect
    async def setup_only():
        events[:] = [*events, "SETUP ONLY"]

    def handle_click(e):
        set_render_num(render_num + 1)

    return div[
        button(id="rerender", onClick=handle_click),
        div(id="events")[",".join(events[:])],
    ]
