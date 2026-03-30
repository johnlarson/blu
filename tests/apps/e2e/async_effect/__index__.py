from blu import client, use_effect, use_ref, use_state
from blu.html import button, div

__client__ = True


def __page__():
    return MyClientElement


@client
def MyClientElement():
    render_id, rerender = use_state(0)
    events_ref = use_ref([])
    events_div_ref = use_ref()

    def _sync_events_div():
        from js import document

        t = ",".join(events_ref[:])
        document.title = f"blu-async-effect:{t}"
        el = events_div_ref[:]
        if el is not None:
            el.textContent = t

    @use_effect
    async def setup_teardown():
        events_ref[:] = [*events_ref[:], "SETUP"]
        _sync_events_div()
        yield
        events_ref[:] = [*events_ref[:], "TEARDOWN"]
        _sync_events_div()

    @use_effect
    async def setup_only():
        events_ref[:] = [*events_ref[:], "SETUP ONLY"]
        _sync_events_div()

    def handle_rerender(_):
        rerender(render_id + 1)

    return (
        button(id="rerender", onClick=handle_rerender)["rerender"],
        div(id="events", ref=events_div_ref)[""],
    )
